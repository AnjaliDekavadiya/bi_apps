# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ConstructionLog(models.Model):
    _name = 'construction.daily.log'
    _description = 'Construction Log'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    custom_user_id = fields.Many2one(
        'res.users', 
        string='User',
        required=True
    )
    custom_project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=False
    )
    custom_task_id = fields.Many2many(
        'project.task',
        string='Job Order',
        required=False,
    )
    custom_timesheet_line_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic Account"
    )
    custom_employee_id = fields.Many2one(
        'hr.employee', 
        required=False,
        string="Employee"
    )
    custom_department_id = fields.Many2one(
        'hr.department', 
        string='Department',
        required=False, 
    )
    custom_manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        required=False,
        copy=False,
    )
    custom_date = fields.Date(
        string="Date",
        required=True,
        default=fields.date.today()
    )
    name = fields.Char(
        string="Name",
        compute='_compute_name',
    )
    construction_daily_log_custom = fields.Html(
        string="Construction Daily Log"
    )
    sub_contractors = fields.Html(
        string="Subcontractors"
    )
    custom_activities = fields.Html(
        string="Activities"
    )
    custom_trades = fields.Html(
        string="Trades"
    )
    custom_tests_inspections = fields.Html(
        string="Tests Inspections"
    )
    custom_visitors = fields.Html(
        string="Visitors"
    )
    custom_notes = fields.Html(
        string="Notes"
    )
    custom_equipment_rentals = fields.Html(
        string="Equipment Rentals"
    )
    custom_material_deliveries = fields.Html(
        string="Material Deliveries"
    )
    custom_company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.user.company_id,
    )

    @api.onchange('custom_user_id','custom_employee_id')
    def _onchange_user_employee(self):
        for rec in self:
            rec.custom_employee_id = rec.custom_user_id.employee_id.id
            rec.custom_department_id = rec.custom_employee_id.department_id.id
            rec.custom_manager_id = rec.custom_employee_id.parent_id.id

    @api.depends('custom_date','custom_user_id')
    def _compute_name(self):
        for rec in self:
            rec.name = False
            date = datetime.strptime(str(rec.custom_date), tools.DEFAULT_SERVER_DATE_FORMAT).date()
            user_lang = self.env['res.lang'].search([('code','=',self.env.user.lang)],limit=1)
            date = date.strftime(user_lang.date_format)
            if rec.custom_date and rec.custom_user_id:
                rec.name = rec.custom_user_id.name +  ' / '  + date

    def action_daily_log_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            # template_id = ir_model_data.get_object_reference('construction_daily_logs', 'email_template_construction_daily_log_custom')[1]
            template_id = self.env['ir.model.data']._xmlid_to_res_id('construction_daily_logs.email_template_construction_daily_log_custom', raise_if_not_found=False)
        except ValueError:
            template_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'construction.daily.log',
            # 'default_res_id': self.ids[0],
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:       