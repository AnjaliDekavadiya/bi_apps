# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, api,fields, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class SubscriptionContractUpsell(models.TransientModel):
    
    _name = 'contract.upsell'

    contract_upsell_line_ids = fields.One2many(
        'contract.upsell.line',
        'contract_upsell_id',
        string='Contract Upsell',
    )
    
    reason = fields.Text(
        string='Reason',
        required=True
    )

    #@api.multi
    def add_new_contract(self):
        context = dict(self._context or {})
        active_id = self._context.get('active_id', False)
        analyticsaleAccount = self.env['analytic.sale.order.line']
        
        for rec in self:
            for contract_upsell_line in rec.contract_upsell_line_ids:
                if contract_upsell_line.product_qty == 0:
                    raise UserError(('Enter Product Quantity.'))
                else:
                    account_analytic_account_id = self.env['account.analytic.account'].browse(active_id)
                    account_sale_lines =  account_analytic_account_id.subscription_product_line_ids.filtered(lambda l: l.product_id.id == contract_upsell_line.product_id.id and l.product_uom.id == contract_upsell_line.product_uom.id)
                    if account_sale_lines:
                        for account_lines in account_sale_lines:
                            account_sale_lines.write({
                                'product_uom_qty': account_lines.product_uom_qty + contract_upsell_line.product_qty
                            })
                            
                            upsell_history_lines = {
                                'contract_line_id' : account_sale_lines.id,
                                'upsell_contract_type': 'update',
                                'old_product_qty': account_lines.product_uom_qty - contract_upsell_line.product_qty,
                                'update_product_qty' : account_lines.product_uom_qty,
                                'reason_contract': rec.reason,
                            }
                                
                            account_analytic_account_id.write({
                                'upsell_history_id':[(0, 0, upsell_history_lines)]
                            })
                            
                    else:
                        analytic_sale_order_line = {
                                    'product_id': contract_upsell_line.product_id.id,
                                    'product_uom':  contract_upsell_line.product_uom.id,
                                    'product_uom_qty': contract_upsell_line.product_qty,
                                    'name' : contract_upsell_line.product_id.description,
                                    'subscription_product_line_id': account_analytic_account_id.id,
                                    'price_unit': contract_upsell_line.product_id.lst_price,
                        }
                                    
                        analytic_sale_order_line = analyticsaleAccount.create(analytic_sale_order_line)
#                        analytic_sale_order_line.write({
#                            'product_uom': contract_upsell_line.product_uom.id,
#                        })
                        
                        upsell_history_lines = {
                                'contract_line_id' : analytic_sale_order_line.id,
                                'upsell_contract_type': 'new',
                                'old_product_qty': analytic_sale_order_line.product_uom_qty,
                                'update_product_qty' : 0,
                                'reason_contract': rec.reason,
                        }
                        
                        account_analytic_account_id.write({
                            'upsell_history_id':[(0, 0, upsell_history_lines)]
                        })
                        
    #@api.multi
    def add_new_quotation(self):
        context = dict(self._context or {})
        active_id = self._context.get('active_id', False)
        saleObj = self.env['sale.order']
        account_analytic_account_id = self.env['account.analytic.account'].browse(active_id)
        
        for rec in self:
            vals_list = []
            for contract_upsell_line in rec.contract_upsell_line_ids:
                sale_order_lines_vals = {
                    'product_id': contract_upsell_line.product_id.id,
                    'product_uom':  contract_upsell_line.product_uom.id,
                    'product_uom_qty': contract_upsell_line.product_qty,
                    'name' : contract_upsell_line.product_id.name,
                }
                vals_list.append((0, 0,sale_order_lines_vals))
                
            sale_order_vals = {
                     'partner_id': account_analytic_account_id.partner_id.id,
                     'validity_date': datetime.today(),
                     'analytic_account_id': account_analytic_account_id.id,
                     'order_line':vals_list,
                     'is_upsell_quotation':True,
                     'note': rec.reason,
                }
            sale_order_id = saleObj.create(sale_order_vals)
            
            upsell_history_lines = {
                'sale_order_id':sale_order_id.id,
                'reason_contract': rec.reason,
                'upsell_contract_type':'sale_type',
            }
                        
            account_analytic_account_id.write({
                'upsell_history_id':[(0, 0, upsell_history_lines)]
            })
            
            
            if sale_order_id:
                action = self.env.ref("sale.action_quotations_with_onboarding").read([])[0]
                action['domain'] = [('id', '=', sale_order_id.id)]
                return action
                
                
                        
                    
                    
class SubscriptionContractUpsellLine(models.TransientModel):
     
    _name = 'contract.upsell.line'

    product_id = fields.Many2one(
        'product.product', 
        string='Product',
        required=True,
    )
    
    product_qty = fields.Float(
        string='Quantity',
        required=True,
    )
    
    product_uom = fields.Many2one(
        'uom.uom', 
        string='Unit of Measure',
        required=True,
    )
    
    contract_upsell_id = fields.Many2one(
        'contract.upsell', 
        string='Contract Upsell',
        copy=False,
    )
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
    
