# -*- coding: utf-8 -*-


from odoo import models, fields, api

class ServiceSupportType(models.Model):
    _name = 'service.support.type'
    _description = "Service Support Type"
    
    name = fields.Char(
        string='Name',
        required=True
    )

class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'

    @api.depends('timesheet_line_ids','timesheet_line_ids.amount')
    def _compute_timesheet_cost_amount(self):
        for line in self:
            line.timesheet_cost_amount = abs(sum(p.amount for p in line.timesheet_line_ids))
            
    
    service_support_type_id = fields.Many2one(
        'service.support.type',
        string='Billing Term',
        copy=True
    )
    customer_billing_type = fields.Selection(
        related='analytic_account_id.customer_billing_type',
        store=True,
        string='Customer Billing Type',
    )
    timesheet_cost_amount = fields.Float(
        string="Total Timesheet Cost",
        compute="_compute_timesheet_cost_amount",
        copy=True,
        store=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order', 
        string='Sales Order',
        copy=False
    )
    purchase_id = fields.Many2one(
        'purchase.order', 
         string='Purchase Order',
         copy=False 
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        string="Currency",
        default=lambda self: self.env.user.company_id.currency_id.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
