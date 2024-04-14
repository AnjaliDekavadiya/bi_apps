# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends(
        'prepared_hours_ids',
        'prepared_hours_ids.sale_order_id',
        'prepared_hours_ids.sale_order_id.amount_untaxed'
    )
    def _compute_sale_cost_amount(self):
        for line in self:
            line.sale_cost_amount = sum(p.sale_order_id.amount_untaxed for p in line.prepared_hours_ids)

    @api.depends(
        'helpdesk_support_ids',
        'helpdesk_support_ids.timesheet_cost_amount'
    )
    def _compute_employee_cost_amount(self):
        for line in self:
            line.emplyee_cost_amount = sum(p.timesheet_cost_amount for p in line.helpdesk_support_ids)

    @api.depends(
        'sale_cost_amount',
        'emplyee_cost_amount'
    )
    def _compute_total_cost_amount(self):
        for rec in self:
            rec.balance_cost_amount = rec.sale_cost_amount - rec.emplyee_cost_amount
            
            
    customer_billing_type = fields.Selection(
        [('prepared_hours','Prepaid Hours'),
         ('postpaid_hours','Postpaid Hours')],
        string='Customer Billing Type',
    )
    sale_cost_amount = fields.Float(
        string="Total Sales Amount",
        compute="_compute_sale_cost_amount",
        copy=True,
        store=True,
    )
    helpdesk_support_ids = fields.One2many(
        'helpdesk.support',
        'analytic_account_id',
        string='Helpdesk Support',
        copy=False,
        readonly=True,
    )
    emplyee_cost_amount = fields.Float(
        string="Total Helpdesk Cost Amount",
        copy=True,
        compute="_compute_employee_cost_amount",
        store=True,
    )
    balance_cost_amount = fields.Float(
        string="Balance Amount",
        copy=True,
        compute="_compute_total_cost_amount",
        store=True,
    )
    

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    
    customer_billing_type = fields.Selection(
        [('prepared_hours','Prepaid Hours'),
         ('postpaid_hours','Postpaid Hours')],
        string='Customer Billing Type',
    )
    service_support_type_id = fields.Many2one(
        'service.support.type',
        string='Billing Term'
    )
    
    @api.model
    def default_get(self, fields):
        ctx = dict(self.env.context)
        res = super(AccountAnalyticLine, self).default_get(fields)
        if ctx.get('default_customer_billing_type') == 'postpaid_hours':
            res['billable'] = False
        else:
            res['billable'] = True
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:      
