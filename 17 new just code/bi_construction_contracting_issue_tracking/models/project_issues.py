# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import datetime, timedelta, date
from odoo import http, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class ProjectIssues(models.Model):
    _inherit = "project.issue"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            ss = self.env['project.task.type'].search([])
            lst1 = []
            if vals['project_id']:
                proj = self.env['project.project'].browse(int(vals['project_id']))
                if proj.type_ids.ids != []:
                    lst1 = proj.type_ids.ids
                    vals['stage_id'] = lst1[0]
            if vals.get('user_id') and not vals.get('date_open'):
                vals['date_open'] = fields.Datetime.now()

            create_date = fields.Date.from_string(vals['date_create'])

            if create_date:
                if create_date > date.today():
                    raise UserError(
                        _('Create Date Must be less Than Current Date'))

            vals['sequence'] = self.env['ir.sequence'].next_by_code('issue.req.seq') or 'ISSUE-000'

            result = super(ProjectIssues, self).create(vals_list)
            return result

    sequence = fields.Char(string='Sequence', readonly=True)
    type_of_issue_id = fields.Many2one('type.issue', string="Type of issue")
    type_of_issue_subject_id = fields.Many2one('type.issue.subject', string="Type of issue Subject")
    construction_team_id = fields.Many2one('issue.teams', string='Construction Team')
    team_leader_id = fields.Many2one('res.users', string="Team Leader", related='construction_team_id.leader',
                                     readonly=True)
    job_order_id = fields.Many2one('job.order', string="Job Order")
    job_cost_sheet_id = fields.Many2one('job.cost.sheet', string="Job Cost Sheet")
    job_cost_line_id = fields.Many2one('job.cost.line', string="Job Cost Line")
    department_id = fields.Many2one('hr.department', string="Department")
    category_id = fields.Many2one('categories', string='Category')
    phone = fields.Char(string="Phone")
    images_ids = fields.One2many('ir.attachment', 'proj_issue_id', 'Images')
    attachment_count = fields.Integer('Attachments', compute='_get_attachment_count')
    invoice_count = fields.Integer('Invoices', compute='_get_invoice_count')
    is_closed = fields.Boolean("Is issue closed?")
    invoice_line_ids = fields.One2many('add.invoice', 'proj_issue', string="Invoice")
    send_url = fields.Char("Send url")
    apply_timesheet_invoice = fields.Boolean('Apply Timesheet Invoice')
    select_cost = fields.Selection([('employee_cost', 'Employee Cost'), ('manual_cost', 'Manual Cost')], 'Select Cost')
    employee_cost = fields.Boolean("Employee Cost")
    manual_cost = fields.Boolean("Manual Cost")
    enter_manual_cost = fields.Float(" Add Manual Cost")
    status = fields.Selection([('to_do', 'To do'), ('in_progress', 'In Progress'), ('done', 'Done')], readonly=True,
                              string='Status', copy=False, index=True, tracking=True, default='to_do')

    def set_close(self):
        self.send_url = http.request.httprequest.host_url
        su_id = self.env.user.company_id
        template_id = self.env['ir.model.data']._xmlid_lookup(
            'bi_construction_contracting_issue_tracking.email_template_project_issue')[1]
        email_template_obj = self.env['mail.template'].browse(template_id)
        fields = ['subject', 'body_html', 'email_from', 'email_to',
                  'partner_to', 'email_cc', 'reply_to', 'scheduled_date']
        if email_template_obj:
            values = email_template_obj._generate_template(self.ids, fields)
            for res_id, values in values.items():
                values['email_from'] = self.env['res.users'].browse(
                    self.env['res.users']._context['uid']).partner_id.email
                values['email_to'] = self.partner_id.email
                values['res_id'] = False
                values['author_id'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.sudo().create(values)
                if msg_id:
                    mail_mail_obj.send([msg_id])

    def create_invoice(self):
        inv_line = []
        timesheet_invoice_line = []
        main_lines = []

        for line in self.timesheet_ids:

            if self.apply_timesheet_invoice == True and self.select_cost == 'employee_cost':
                line.amount = line.employee_id.timesheet_cost
            if self.apply_timesheet_invoice == True and self.select_cost == 'manual_cost':
                line.amount = self.enter_manual_cost

            if self.apply_timesheet_invoice == True:
                timesheet_invoice_line.append((0, 0, {'product_id': line.job_cost_line_id.product_id.id,
                                                      'name': line.name,
                                                      'product_uom_id': line.product_uom_id.id,
                                                      'price_unit': line.amount,
                                                      'quantity': line.unit_amount,

                                                      }))

        for line in self.invoice_line_ids:
            if line.is_created == True:
                line_account_id = False
                if line.product_id.id:
                    line_account_id = line.product_id.categ_id.property_account_income_categ_id.id
                if not line_account_id:
                    raise UserError(
                        _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') % \
                        (line.product_id.name,))

                inv_line.append((0, 0, {'product_id': line.product_id.id,
                                        'name': line.name,
                                        'product_uom_id': line.uom_id.id,
                                        'price_unit': line.price_unit,
                                        'quantity': line.quantity,

                                        }))

        journal = self.env['account.journal'].search([('type', '=', 'sale')])
        account_inv = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'journal_id': journal.id or False,
            'move_type': 'out_invoice',
            'invoice_origin': self.sequence,
            'currency_id': self.partner_id.currency_id.id,
            'invoice_line_ids': timesheet_invoice_line + inv_line,
            'project_issue': self.id,
            'invoice_date': str(datetime.now()),
        })

    @api.onchange('job_cost_sheet_id')
    def onc_order(self):
        self.job_order_id = self.job_cost_sheet_id.job_order_id
        self.analytic_id = self.job_cost_sheet_id.analytic_ids

    @api.onchange('construction_team_id')
    def onc_team(self):
        self.team_leader_id = self.construction_team_id.leader

    @api.onchange('project_id')
    def onc_project(self):
        self.stage_id = ""
        self.analytic_id = self.project_id.analytic_account_id
        for line in self.timesheet_ids:
            line.project_id = self.project_id

    def _get_attachment_count(self):
        self.attachment_count = None
        for i in self:
            attachment_ids = self.env['ir.attachment'].search([('proj_issue_id', '=', i.id)])
            i.attachment_count = len(attachment_ids)

    def attachment_on_issue_req_button(self):
        self.ensure_one()
        return {
            'name': 'Attachment Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('proj_issue_id', '=', self.id)],
        }

    def _get_invoice_count(self):
        self.invoice_count = None
        for i in self:
            invoice_ids = self.env['account.move'].search([('project_issue', '=', i.id)])
            i.invoice_count = len(invoice_ids)

    def invoice_button(self):
        self.ensure_one()
        views = [(self.env.ref('account.view_invoice_tree').id, 'tree'),
                 (self.env.ref('account.view_move_form').id, 'form')]
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'view_id': False,
            'views': views,
            'res_model': 'account.move',
            'domain': [('project_issue', '=', self.id)],
        }

    @api.onchange('status')
    def onc_status(self):
        self.date_last_stage_update = fields.Datetime.now()

    def write(self, vals):
        create_date = fields.Date.from_string(vals.get('date_create'))

        if create_date:
            if create_date > date.today():
                raise UserError(
                    _('Create Date Must be less Than Current Date'))

        if 'is_closed' in vals:
            vals.update({'status': 'done', 'date_closed': fields.Datetime.now()})
        now = fields.Datetime.now()
        if vals.get('user_id') and 'date_open' not in vals:
            vals['date_open'] = now
        result = super(ProjectIssues, self).write(vals)

        return result


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    proj_issue_id = fields.Many2one('project.issue', ' Issue Request ')


class InheritPartner(models.Model):
    _inherit = 'res.partner'

    price = fields.Float("Price/Rate (Company Currency)")
    product_id = fields.Many2one('product.product', string='Product')
    project_issue_ids = fields.One2many('project.issue', 'partner_id', string='partner_id', auto_join=True)
    proj_issue_count = fields.Integer('Project Issues', compute='_get_issue_count')

    def _get_issue_count(self):
        self.proj_issue_count = None
        for i in self:
            issue_ids = self.env['project.issue'].search([('partner_id', '=', i.id)])
            i.proj_issue_count = len(issue_ids)

    def project_issue_req_button(self):
        self.ensure_one()
        return {
            'name': 'Project Issue Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.issue',
            'domain': [('partner_id', '=', self.id)],
        }


class ProjectInherit(models.Model):
    _inherit = "project.project"

    price = fields.Float(related="partner_id.price", string="Price/Rate (Company Currency)")
    product_id = fields.Many2one('product.product', string='Product', related="partner_id.product_id", )


class InheritInvoice(models.Model):
    _inherit = "account.move"

    project_issue = fields.Many2one('project.issue', string="Project Issue")


class InheritInvoiceLine(models.Model):
    _inherit = "account.move.line"
    proj_issue = fields.Many2one('project.issue', string="Project Issue")
    is_created = fields.Boolean(string="Is Invoice Create")


class AddInvoiceLine(models.Model):
    _name = "add.invoice"
    _description = "Add Invoice"

    partner_id = fields.Many2one('res.partner', string="Partner")
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Char('Description')
    account_id = fields.Many2one('account.account', string="Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    currency_id = fields.Many2one('res.currency', string="Currency")
    line_account_id = fields.Many2one('account.account', string=" Account")
    quantity = fields.Float("Quantity")
    price_unit = fields.Float("Price")
    uom_id = fields.Many2one('uom.uom', "Unit of Measure")
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    is_created = fields.Boolean("Is Invoice Create")
    proj_issue = fields.Many2one('project.issue')

    @api.onchange('product_id')
    def onc_product(self):
        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id
        self.price_unit = self.product_id.lst_price
        self.analytic_account_id = self.proj_issue.analytic_id
        self.quantity = 1.0


class InheritAccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    proj_issue_id = fields.Many2one('project.issue', string=" Project Issue")
    time_in = fields.Float("Time In")
    time_out = fields.Float("Time out")
    job_cost_sheet_id = fields.Many2one('job.cost.sheet', string="Job Cost Sheet")
    job_cost_line_id = fields.Many2one('job.cost.line', string="Job Cost Line")


class JobCostLine(models.Model):
    _inherit = "job.cost.line"
    _rec_name = "job_type_id"


class task_wizard(models.TransientModel):
    _inherit = 'task.wizard'

    @api.model
    def default_get(self, flds):
        result = super(task_wizard, self).default_get(flds)
        issue_id = self.env['project.issue'].browse(self._context.get('active_id'))
        result['name'] = issue_id.name
        result['description'] = issue_id.description
        result['project_id'] = issue_id.project_id.id
        result['user_id'] = issue_id.user_id.id
        return result

    def create_task(self):
        project_issue_id = self.env['project.issue'].browse(self._context.get('active_id'))
        list_of_tag = []
        list_of_line = []
        project_task_obj = self.env['project.task']
        for tag in project_issue_id.tag_ids:
            list_of_tag.append(tag.id)
        for line in project_issue_id.timesheet_ids:
            list_of_line.append((0, 0, {'date': line.date,
                                        'employee_id': line.employee_id.id,
                                        'name': line.name,
                                        'unit_amount': line.unit_amount,
                                        'account_id': project_issue_id.analytic_id.id

                                        }))
        vals = {
            'name': self.name,
            'project_id': self.project_id.id,
            'user_ids': self.user_id,
            'tag_ids': [(6, 0, list_of_tag)],
            'support_id': project_issue_id.id,
            'description': self.description,
            'planned_hours': self.planned_hours,
        }
        project_issue_id.write({'status': 'in_progress'})
        project_task = project_task_obj.create(vals)
        project_task.write({'timesheet_ids': list_of_line})
        return project_task
