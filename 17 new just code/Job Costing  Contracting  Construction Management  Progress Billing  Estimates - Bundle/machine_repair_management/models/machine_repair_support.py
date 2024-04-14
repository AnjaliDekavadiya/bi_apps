# -*- coding: utf-8 -*-

import time
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MachineRepairSupport(models.Model):
    _name = 'machine.repair.support'
    _description = 'Machine Repair Support'
    _order = 'id desc'
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'format.address.mixin','portal.mixin']

    
    @api.model
    def create(self, vals):

        if vals.get('custome_client_user_id', False):
            client_user_id = self.env['res.users'].browse(int(vals.get('custome_client_user_id')))
            if client_user_id:
                vals.update({'company_id': client_user_id.company_id.id})
        else:
            vals.update({'custome_client_user_id': self.env.user.id})

        if vals.get('name', False):
            if not vals.get('name', 'New') == 'New':
                vals['subject'] = vals['name']
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('machine.repair.support') or 'New'
        
        if vals.get('partner_id', False):
            if 'phone' and 'email' not in vals:
                partner = self.env['res.partner'].sudo().browse(vals['partner_id'])
                if partner:
                    vals.update({
                        'email': partner.email,
                        'phone': partner.phone,
                    })
        return super(MachineRepairSupport, self).create(vals)
    
#    @api.multi odoo13
    @api.depends('timesheet_line_ids.unit_amount')
    def _compute_total_spend_hours(self):
        for rec in self:
            spend_hours = 0.0
            for line in rec.timesheet_line_ids:
                spend_hours += line.unit_amount
            rec.total_spend_hours = spend_hours
    
    @api.onchange('project_id')
    def onchnage_project(self):
        for rec in self:
            rec.analytic_account_id = rec.project_id.analytic_account_id
          
#    @api.one odoo13
    def set_to_close(self):
        if self.is_close != True:
            self.is_close = True
            self.close_date = fields.Datetime.now()#time.strftime('%Y-%m-%d')
            self.state = 'closed'
            template = self.env.ref('machine_repair_management.email_template_machine_ticket')
            template.send_mail(self.id)
            
#    @api.one odoo13
    def set_to_reopen(self):
        self.state = 'work_in_progress'
        if self.is_close != False:
            self.is_close = False

#    @api.multi odoo13
    def create_machine_diagnosys(self):
        for rec in self:
            name = ''
            if rec.subject:
                name = rec.subject +'('+rec.name+')'
            else:
                name = rec.name
            task_vals = {
                'name' : str(name),
                # 'user_id' : rec.user_id.id,
                # 'activity_user_id': rec.user_id.id,
                'user_ids': [rec.user_id.id or self.env.user.id],
                # 'user_ids' : [(4, rec.user_id.id)],
                'date_deadline' : rec.close_date,
                'project_id' : rec.project_id.id,
                'partner_id' : rec.partner_id.id,
                'description' : rec.description,
                'machine_ticket_id' : rec.id,
                'task_type': 'diagnosys',
            }
            task_id= self.env['project.task'].sudo().create(task_vals)
        # action = self.env.ref('machine_repair_management.action_view_task_diagnosis')
        # result = action.sudo().read()[0]
        result = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_view_task_diagnosis")
        result['domain'] = [('id', '=', task_id.id)]
        return result

#    @api.multi odoo13
    def create_work_order(self):
        for rec in self:
            work_order_name = ''
            if rec.subject:
                work_order_name = rec.subject +'('+rec.name+')'
            else:
                work_order_name = rec.name
            task_vals = {
#            'name' : rec.subject +'('+rec.name+')', odoo13
            'name' : work_order_name,
            # 'user_id' : rec.user_id.id,
            # 'activity_user_id': rec.user_id.id,
            'user_ids': [rec.user_id.id or self.env.user.id],
            # 'user_ids' : [(4, rec.user_id.id)],
            'date_deadline' : rec.close_date,
            'project_id' : rec.project_id.id,
            'partner_id' : rec.partner_id.id,
            'description' : rec.description,
            'machine_ticket_id' : rec.id,
            'task_type': 'work_order',
            }
            task_id= self.env['project.task'].sudo().create(task_vals)
        # action = self.env.ref('machine_repair_management.action_view_task_workorder')
        # result = action.sudo().read()[0]
        result = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_view_task_workorder")
        result['domain'] = [('id', '=', task_id.id)]
        return result

    @api.onchange('product_id')
    def onchnage_product(self):
        for rec in self:
            rec.brand = rec.product_id.brand
            # rec.color = rec.product_id.color odoo13
            rec.color = rec.product_id.color_custom
            rec.model = rec.product_id.model
            rec.year = rec.product_id.year
    
    name = fields.Char(
        string='Number', 
        required=False,
        default='New',
        copy=False, 
        readonly=True, 
    )
    state = fields.Selection(
        [('new','New'),
         ('assigned','Assigned'),
         ('work_in_progress','Work in Progress'),
         ('needs_more_info','Needs More Info'),
         ('needs_reply','Needs Reply'),
         ('reopened','Reopened'),
         ('solution_suggested','Solution Suggested'),
         ('closed','Closed')],
        tracking=True,
        default='new',
        copy=False, 
    )
    email = fields.Char(
        string="Email",
        required=False
    )
    phone = fields.Char(
        string="Phone"
    )
    category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('support', 'Support')],
        string='Category',
    )
    subject = fields.Char(
        string="Subject"
    )
    description = fields.Text(
        string="Description"
    )
    priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
        string='Priority',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    request_date = fields.Datetime(
        string='Create Date',
        # default=fields.Datetime.now,
        default=lambda self: fields.Datetime.now(),
        copy=False,
    )
    close_date = fields.Datetime(
        string='Close Date',
    )
    user_id = fields.Many2one(
        'res.users',
        string='Technician',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )
    timesheet_line_ids = fields.One2many(
        'account.analytic.line',
        'repair_request_id',
        string='Timesheets',
    )
    is_close = fields.Boolean(
        string='Is Ticket Closed ?',
        tracking=True,
        default=False,
        copy=False,
    )
    total_spend_hours = fields.Float(
        string='Total Hours Spent',
        compute='_compute_total_spend_hours'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    team_id = fields.Many2one(
        'machine.support.team',
        string='Machine Repair Team',
        default=lambda self: self.env['machine.support.team'].sudo()._get_default_team_id(user_id=self.env.uid),
    )
    team_leader_id = fields.Many2one(
        'res.users',
        string='Team Leader',
    )
    journal_id = fields.Many2one(
        'account.journal',
         string='Journal',
     )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        readonly = True,
    )
    is_task_created = fields.Boolean(
        string='Is Task Created ?',
        default=False,
    )
    company_id = fields.Many2one(
        'res.company', 
        default=lambda self: self.env.user.company_id, 
        string='Company',
        readonly=False,
#        readonly=True,
     )
    comment = fields.Text(
        string='Customer Comment',
        readonly=True,
    )
    rating = fields.Selection(
        [('poor', 'Poor'),
        ('average', 'Average'),
        ('good', 'Good'),
        ('very good', 'Very Good'),
        ('excellent', 'Excellent')],
        string='Customer Rating',
        readonly=True,
    )
    product_category = fields.Many2one(
        'product.category',
        string="Product Category"
    )
    product_id = fields.Many2one(
        'product.product',
        domain="[('is_machine', '=', True)]",
        string="Product"
    )
    brand = fields.Char(
        string = "Brand"
    )
    color = fields.Char(
        string = "Color"
    )
    model = fields.Char(
        string="Model"
    )
    year = fields.Char(
        string="Year"
    )
    accompanying_items = fields.Text(
        string="Accompanying Items",
    )
    damage = fields.Text(
        string="Damage",
    )
    warranty = fields.Boolean(
        string="Warranty",
    )
    img1 = fields.Binary(
        string="Images1",
    )
    img2 = fields.Binary(
        string="Images2",
    )
    img3 = fields.Binary(
        string="Images3",
    )
    img4 = fields.Binary(
        string="Images4",
    )
    img5 = fields.Binary(
        string="Images5",
    )
    repair_types_ids = fields.Many2many(
        'repair.type',
        string="Repair Type"
    )
    problem = fields.Text(
       string="Problem",
    )
    cosume_part_ids = fields.One2many(
      'product.consume.part',
      'machine_id',
      string="Produ Ctconsume Part"
    )
    nature_of_service_id = fields.Many2one(
        'service.nature',
        string="Nature Of service"
    )
    lot_id = fields.Many2one(
        # 'stock.production.lot',
        'stock.lot',
        string="Lot"
    )
    website_brand = fields.Char(
        string = "Website Brand"
    )
    website_model = fields.Char(
        string = "Website Model"
    )
    website_year = fields.Char(
        string = "Website Year"
    )
#     @api.multi
#     @api.depends('analytic_account_id')
#     def compute_total_hours(self):
#         total_remaining_hours = 0.0
#         for rec in self:
#             rec.remaining_hours = rec.analytic_account_id.remaining_hours
#     
    total_consumed_hours = fields.Float(
        string='Total Consumed Hours',
#         compute='compute_total_hours',
#         store=True,
    )
    
    custome_client_user_id = fields.Many2one(
        'res.users',
        string="Ticket Created User",
        readonly = True,
        # track_visibility='always'
        tracking=True,
    )
    
#    @api.multi odoo13
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.email = rec.partner_id.email
                rec.phone = rec.partner_id.phone

#    @api.multi odoo13
    @api.onchange('product_category')
    def product_id_change(self):
        return {'domain':{'product_id':[('is_machine', '=', True),('categ_id', '=', self.product_category.id)]}}

#    @api.multi odoo13
    @api.onchange('team_id')
    def team_id_change(self):
        for rec in self:
            rec.team_leader_id = rec.team_id.leader_id.id
    
#    @api.one odoo13
    def unlink(self):
        for rec in self:
            if rec.state != 'new':
                raise UserError(_('You can not delete record which are not in draft state.'))
        return super(MachineRepairSupport, self).unlink()
    
#    @api.multi odoo13
    def show_machine_diagnosys_task(self):
        self.ensure_one()
        # for rec in self:
            # res = self.env.ref('machine_repair_management.action_view_task_diagnosis')
            # res = res.sudo().read()[0]
        res = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_view_task_diagnosis")
        res['domain'] = str([('task_type','=','diagnosys'), ('machine_ticket_id', '=', self.id)])
        res['context'] = {'default_machine_ticket_id': self.id, 'default_task_type': 'diagnosys'}
        return res
    
#    @api.multi odoo13
    def show_work_order_task(self):
        self.ensure_one()
        # for rec in self:
        #     res = self.env.ref('project.action_view_task')
        #     res = res.sudo().read()[0]
        res = self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
        res['domain'] = str([('task_type','=','work_order'), ('machine_ticket_id', '=', self.id)])
        res['context'] = {'default_machine_ticket_id': self.id, 'default_task_type': 'work_order'}
        return res

    def get_access_action(self):
        website_id = self.env['website'].search([('company_id','=',self.company_id.id)],limit=1)
        if website_id.domain:
            if website_id.domain.endswith('/'):
                domain_name = website_id.domain
                url = domain_name + '/machine_repair_email/feedback/' + str(self.id)
                return url
            else:
                domain = website_id.domain
                url = domain + '/machine_repair_email/feedback/' + str(self.id)
                return url
        else:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url = base_url + '/machine_repair_email/feedback/' + str(self.id)
            return url

class HrTimesheetSheet(models.Model):
    _inherit = 'account.analytic.line'

#     support_request_id = fields.Many2one(
#         'machine.repair.support',
#         domain=[('is_close','=',False)],
#         string='Machine Repair Support',
#     )
    billable = fields.Boolean(
        string='Chargable?',
        default=True,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
