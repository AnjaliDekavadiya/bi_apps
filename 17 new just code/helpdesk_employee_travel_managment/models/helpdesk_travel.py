# -*- coding: utf-8 -*-

from odoo import api, fields, models

class EmployeeTravelRequest(models.Model):
    _inherit = 'employee.travel.request'

    helpdesk_support_id = fields.Many2one(
        'helpdesk.support',
        'Helpdesk Support',
    )

class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'

    # @api.multi
    def action_view_travel_request(self):
        self.ensure_one()
        # action = self.env.ref('employee_travel_managment.travel_request_action').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('employee_travel_managment.travel_request_action')
        # action['domain'] = str([('helpdesk_support_id', 'in', self.ids)])
        action['domain'] = str([('helpdesk_support_id', '=', self.id)])
        cotext =  self.env.context.copy()
        cotext.update({'default_helpdesk_support_id': self.id,
                             'default_company_id':self.company_id.id,
                             'default_currency_id':self.env.user.company_id.currency_id.id,
                             'default_project_id':self.project_id.id,
                             'default_department_id':self.department_id.id,
                             'default_analytic_account_id':self.analytic_account_id.id,})
        action['context'] = cotext
        return action
