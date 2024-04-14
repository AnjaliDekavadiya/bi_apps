# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class inspection_value(models.Model):
    _name = 'inspection.value'
    _description = "inspection value"

    name = fields.Char('Name')
    code = fields.Char('Code')


class inspection_result(models.Model):
    _name = 'inspection.result'
    _description = "inspection result"

    name = fields.Char('Name')
    code = fields.Char('Code')


class inspection_type(models.Model):
    _name = 'inspection.type'
    _description = "inspection type"

    name = fields.Char('Name')
    code = fields.Char('Code')


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    job_inspection_id = fields.Many2one('job.inspection')


class project_project(models.Model):
    _inherit = 'project.project'

    def _get_number_of_inspection(self):
        for project in self:
            inspection_ids = self.env['job.inspection'].search([('project_id', '=', project.id)])
            project.count_of_inspection = len(inspection_ids)

    def button_view_inspection(self):
        inspection_list = []
        inspection_ids = self.env['job.inspection'].search([('project_id', '=', self.id)])
        for ins in inspection_ids:
            inspection_list.append(ins.id)
        context = dict(self._context or {})
        return {
            'name': _('Inspection'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'job.inspection',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', inspection_list)],
            'context': context,
        }
    count_of_inspection = fields.Integer('Inspection', compute='_get_number_of_inspection')


class project_task(models.Model):
    _inherit = 'project.task'

    def _get_number_of_inspection(self):
        for project in self:
            inspection_ids = self.env['job.inspection'].search([('project_id', '=', self.project_id.id)])
            project.count_of_inspection = len(inspection_ids)

    def button_view_inspection(self):
        inspection_list = []
        inspection_ids = self.env['job.inspection'].search([('project_id', '=', self.project_id.id)])
        for ins in inspection_ids:
            inspection_list.append(ins.id)
        context = dict(self._context or {})
        return {
            'name': _('Inspection'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'job.inspection',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', inspection_list)],
            'context': context,
        }
    count_of_inspection = fields.Integer('Inspection', compute='_get_number_of_inspection')


class job_cost_sheet(models.Model):
    _inherit = 'job.cost.sheet'

    def _get_number_of_inspection(self):
        for project in self:
            inspection_ids = self.env['job.inspection'].search([('job_cost_sheet_id', '=', self.id)])
            project.count_of_inspection = len(inspection_ids)

    def button_view_inspection(self):
        inspection_list = []
        inspection_ids = self.env['job.inspection'].search([('job_cost_sheet_id', '=', self.id)])
        for ins in inspection_ids:
            inspection_list.append(ins.id)

        context = dict(self._context or {})
        return {
            'name': _('Inspection'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'job.inspection',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', inspection_list)],
            'context': context,
        }

    count_of_inspection = fields.Integer('Inspection', compute='_get_number_of_inspection')


class job_inspection(models.Model):
    _name = 'job.inspection'
    _description = "job inspection"

    @api.model
    def get_company_id(self):
        company_id = self.env['res.users'].browse(self.env.uid).company_id.id
        return company_id

    sequance = fields.Char('Sequance')
    name = fields.Char('Name')
    project_id = fields.Many2one('project.project', 'Project')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    job_order_id = fields.Many2one('job.order', 'Job Order')
    job_cost_sheet_id = fields.Many2one('job.cost.sheet', 'Job Cost Sheet')
    inspection_type_id = fields.Many2one('inspection.type', 'Inspection Type')
    inspection_start_date = fields.Datetime('Inspection Start Date', default=datetime.now())
    resposible_user = fields.Many2one('res.users', default=lambda self: self.env.uid)
    create_date = fields.Datetime('Create Date', default=datetime.now())
    inspection_location = fields.Char('Inspection Location')
    inspection_resposible = fields.Many2one('res.users', string='Inspection Responsible')
    subcontractor_id = fields.Many2one('res.partner', 'Subcontractor')
    reference_specification = fields.Char('Reference Specification')
    inspection_result_id = fields.Many2one('inspection.result', 'Inspection Result')
    inspection_end_date = fields.Datetime('End Date')
    company_id = fields.Many2one('res.company', default=get_company_id)
    confirmed_by_id = fields.Many2one('res.users', string='Confirmed By', readonly=True, copy=False)
    processed_by_id = fields.Many2one('res.users', string='Processed By', readonly=True, copy=False)
    complete_by_id = fields.Many2one('res.users', string='Complete By', readonly=True, copy=False)
    cancel_by_id = fields.Many2one('res.users', string='Cancel By', readonly=True, copy=False)
    confirm_date = fields.Datetime('Confirm Date', readonly=True, copy=False)
    process_date = fields.Datetime('Process Date', readonly=True, copy=False)
    complete_date = fields.Datetime('Complete Date', readonly=True, copy=False)
    cancel_date = fields.Datetime('Cancel Date', readonly=True, copy=False)
    notes = fields.Text('Note')
    result_description = fields.Text('Description')
    attachment_ids = fields.One2many('ir.attachment', 'job_inspection_id')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('process', 'Process'), ('complete', 'Complete'),
         ('cancel', 'Cancel')], default='draft')
    job_inspection_line_ids = fields.One2many('job.inspection.line', 'job_inspection_id')

    @api.onchange('project_id')
    def change_analytic_account_id(self):
        for rec in self:
            if rec.project_id:
                rec.write({'analytic_account_id': rec.project_id.analytic_account_id})

    def to_confirm(self):
        if self.inspection_start_date and self.inspection_end_date:
            if self.inspection_start_date > self.inspection_end_date:
                raise ValidationError(_('End date is must be greater than Start date'))
        else:
            raise ValidationError(_('Please Enter Date'))

        for job_ins in self:
            job_ins.state = 'confirm'
            job_ins.confirmed_by_id = self.env.uid
            job_ins.confirm_date = datetime.now()

    def to_process(self):
        for job_ins in self:
            job_ins.state = 'process'
            job_ins.processed_by_id = self.env.uid
            job_ins.process_date = datetime.now()

    def to_complete(self):
        for job_ins in self:
            job_ins.state = 'complete'
            job_ins.complete_by_id = self.env.uid
            job_ins.complete_date = datetime.now()

    def to_cancel(self):
        for job_ins in self:
            job_ins.state = 'cancel'
            job_ins.cancel_by_id = self.env.uid
            job_ins.cancel_date = datetime.now()

    def to_set_to_draft(self):
        for job_order in self:
            job_order.state = 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals['inspection_start_date'] and vals['inspection_end_date']:
                if vals['inspection_start_date'] > vals['inspection_end_date']:
                    raise ValidationError(_('End date is must be greater than Start date'))
            else:
                raise ValidationError(_('Please Enter Date'))

            vals['sequance'] = self.env['ir.sequence'].next_by_code('insp_seq') or 'INSPECTION'
        result = super(job_inspection, self).create(vals_list)
        return result


class job_inspection_line(models.Model):
    _name = 'job.inspection.line'
    _description = "job inspection"

    inspection_value_id = fields.Many2one('inspection.value', 'Inspection Value')
    inspection_result_id = fields.Many2one('inspection.result', 'Inspection Result')
    description = fields.Char('Description')
    job_inspection_id = fields.Many2one('job.inspection')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
