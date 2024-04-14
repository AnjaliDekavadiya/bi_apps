# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ContractUpsellHistory(models.Model):

    _name = 'contract.upsell.history'

    contract_line_id = fields.Many2one(
        'analytic.sale.order.line',
        string='Contract Line Reference',
        copy=False,
    )
    
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Account Analytic',
    )
    
    upsell_contract_type = fields.Selection(
        [('new', 'New Contract Line'), 
        ('update', 'Update on Existing'),
        ('sale_type', 'Sales Order')], 
        string='Upsell Type',
    )
    
    old_product_qty = fields.Float(
        string='Previous Quantity',
    )
    
    update_product_qty = fields.Float(
        string='Updated Quantity',
    )
    
    reason_contract = fields.Text(
        string='Reason',
    )
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order Reference',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



            
    
