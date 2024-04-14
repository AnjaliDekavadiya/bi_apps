# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
import psycopg2
import itertools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    dimension_method = fields.Selection([('l_w_h', 'LenghtxWidthxHeight'), ('w_h', 'WidthxHeight')], 'Dimention Method')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'dimension_method': self.dimension_method,
            })
        return invoice_vals

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pro_length = fields.Float('Length')
    pro_width = fields.Float('Width')
    pro_height = fields.Float('Height')
    length_chk = fields.Boolean('Length Checkbox')
    width_chk = fields.Boolean('Length Checkbox')
    height_chk = fields.Boolean('height Checkbox')
    tot_qty = fields.Float(compute='_compute_amount', digits=dp.get_precision('Dim QTY'), string='Dim Qty', readonly=True, store=True)
    label = fields.Char('Label')
    dimension_method = fields.Selection(related='order_id.dimension_method',string="Dimention Method")
    custom_weight = fields.Float(compute='_compute_amount', string='Weight Ea.', readonly=True, store=True)

    def _prepare_procurement_values(self,group_id):
        res = super(SaleOrderLine,self)._prepare_procurement_values(group_id=group_id)
        res.update({
            'pro_length':self.pro_length,
            'pro_width':self.pro_width,
            'pro_height':self.pro_height,
            'length_chk':self.length_chk,
            'width_chk':self.width_chk,
            'height_chk':self.height_chk,
            'label':self.label,
            'tot_qty':self.tot_qty,
            'width':self.width,
            'height':self.height,
            'dimension_method':self.dimension_method,
            'custom_weight':self.custom_weight

            })
        return res
        

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        
        res.update({
            'label':self.label,
            'pro_length':self.pro_length,
            'pro_width':self.pro_width,
            'pro_height':self.pro_height,
            'width':self.width,
            'height':self.height,
            'm2':self.m2,
            'dimension_method':self.dimension_method,
            'custom_weight':self.custom_weight
        })
        return res

    def _prepare_order_line_procurement(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_order_line_procurement(group_id=group_id)
        res.update({
                    'label':self.label,
                    'pro_length':self.pro_length,
                    'pro_width':self.pro_width,
                    'pro_height':self.pro_height,
                    'dimension_method':self.dimension_method,
                    'custom_weight':self.custom_weight
            })
        return res      
   
    @api.onchange('pro_width')
    def onchange_width(self):
        
        if self.pro_width < self.product_id.width_min_2 or self.pro_width > self.product_id.width_max_2:
            warning = "You can only enter width between minimum " + str(self.product_id.width_min_2) + " to maximum " + str(self.product_id.width_max_2) + "feet"
            return {

                'warning': {'title': 'Error!', 'message': warning},
                'value': {
            
                    'pro_width': '',
                            }
            } 

    @api.onchange('width')
    def onchange_for_width(self):
        if self.width < self.product_id.width_min_2 or self.width > self.product_id.width_max_2:
            warning = "You can only enter width between minimum " + str(self.product_id.width_min_2) + " to maximum " + str(self.product_id.width_max_2) + " feet"
            return {
                    'warning': {'title': 'Error!', 'message': warning},
                    'value': {
                              'width': '',
                             }
            }

    @api.onchange('height')
    def onchange_for_height(self):
        if self.height < self.product_id.height_min_3 or self.height > self.product_id.height_max_3:
            warning = "You can only enter height between minimum " + str(self.product_id.height_min_3) + " to maximum " + str(self.product_id.height_max_3) + " feet"
            return {
                    'warning': {'title': 'Error!', 'message': warning},
                    'value': {
                              'height': '',
                             }
            }
    
    @api.onchange('pro_height')
    def onchange_height(self):
       
        if self.pro_height < self.product_id.height_min_3 or self.pro_height > self.product_id.height_max_3:
            warning = "You can only enter height between minimum " + str(self.product_id.height_min_3) + " to maximum " + str(self.product_id.height_max_3) + "feet"
            return {

                'warning': {'title': 'Error!', 'message': warning},
                'value': {
            
                    'pro_height': '',
                            }
            }

    @api.onchange('pro_length')
    def onchange_length(self):
       
        if self.pro_length < self.product_id.len_min_1 or self.pro_length > self.product_id.len_max_1:
            warning = "You can only enter length between minimum " + str(self.product_id.len_min_1) + " to maximum " + str(self.product_id.len_max_1) + "feet"
            return {

                'warning': {'title': 'Error!', 'message': warning},
                'value': {
            
                    'pro_length': '',
                            }
            }

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'pro_width', 'pro_length', 'pro_height')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            tot_qty = tot_weight = subtotal = 1
            if not (line.pro_width or line.pro_height or line.pro_length):
                tot_qty = 1.00
            else:
                tot_qty = line.pro_width * line.pro_height * line.pro_length
            weight = tot_qty * line.product_id.weight
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            quantity=line.product_uom_qty
            if self.env.user.company_id.price_calculation == 'dimension':
                quantity = quantity * line.m2
                quantity = quantity * tot_qty
            tax_results = line.tax_id.compute_all(price, line.order_id.currency_id, quantity, product=line.product_id,
                                                  partner=line.order_id.partner_shipping_id)
            line.update({
                'price_subtotal': tax_results['total_excluded'],
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
                'tot_qty':tot_qty,
                'custom_weight': weight,
            })


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        invoice_vals.update({
            'dimension_method':order.dimension_method,
        })
        return invoice_vals
