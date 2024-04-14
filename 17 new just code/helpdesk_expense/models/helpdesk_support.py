# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'

    expense_count = fields.Integer(
        string='# Expense Count',
        compute='_compute_expense_count', 
        readonly=True, 
        default=0
    )

    @api.depends()
    def _compute_expense_count(self):
        hr_expense = self.env['hr.expense']
        for record in self:
            record.expense_count = hr_expense.search_count([('custom_helpdesk_suppor_id', '=', record.id)])
    
#    @api.multi odoo13
    def open_expense_view(self):
        self.ensure_one()
        # action = self.env.ref('hr_expense.hr_expense_actions_my_unsubmitted').sudo().read()[0]
        # action = self.env.ref('hr_expense.hr_expense_actions_my_all').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('hr_expense.hr_expense_actions_my_all')
        action['domain'] = [('custom_helpdesk_suppor_id', '=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
