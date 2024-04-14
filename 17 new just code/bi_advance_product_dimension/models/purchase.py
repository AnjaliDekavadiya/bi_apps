# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models
from datetime import datetime, timedelta,date
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
import psycopg2
import itertools
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    dimension_method = fields.Selection([('l_w_h', 'LenghtxWidthxHeight'), ('w_h', 'WidthxHeight')], 'Dimention Method')

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals.update({
            'dimension_method' : self.dimension_method , 
            })
        return invoice_vals

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    new_date_planned = fields.Date(string='Delivery Date',store=True, index=True,required=True)
    

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.price_unit = self.product_qty = 0.0
        self.new_date_planned = date.today()

        self._product_id_change()

        self._suggest_quantity()

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            for val in line._prepare_stock_moves(picking):
                val.update({
                        'pro_width':line.pro_width,
                        'pro_height':line.pro_height,
                        'pro_length':line.pro_length,
                        'length_chk':line.length_chk,
                        'width_chk':line.width_chk,
                        'height_chk':line.height_chk,
                        'label':line.label,
                        'tot_qty':line.tot_qty,
                        'width':line.width,
                        'height':line.height,
                        'dimension_method':line.dimension_method,
                        'custom_weight':line.custom_weight,
                    })
                
                done += moves.create(val)
        return done
    
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
            
    @api.depends('product_qty', 'price_unit', 'taxes_id', 'pro_length', 'pro_width', 'pro_height')
    def _compute_amount(self):
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
            quantity=line.product_qty
            if self.env.user.company_id.price_calculation == 'dimension':
                quantity = quantity * line.square_meter
                quantity = quantity * tot_qty

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
                'tot_qty':tot_qty,
                'custom_weight': weight,
            })

    pro_length = fields.Float('Length')
    pro_width = fields.Float('Width')
    pro_height = fields.Float('Height')
    label = fields.Char('Label')
    length_chk = fields.Boolean('Length Checkbox')
    width_chk = fields.Boolean('Length Checkbox')
    height_chk = fields.Boolean('height Checkbox')
    tot_qty = fields.Float(compute='_compute_amount', digits=dp.get_precision('Dim QTY'), string='Dim Qty', readonly=True, store=True)
    dimension_method = fields.Selection(related='order_id.dimension_method',string="Dimention Method")
    custom_weight = fields.Float(compute='_compute_amount', string='Weight Ea.', readonly=True, store=True)

    def _prepare_account_move_line(self,move=False):
        res = super(PurchaseOrderLine,self)._prepare_account_move_line(move)
        res.update({
            'width':self.width, 
            'height':self.height, 
            'pro_width':self.pro_width,
            'pro_height':self.pro_height,
            'pro_length':self.pro_length,
            'length_chk':self.length_chk,
            'width_chk':self.width_chk,
            'height_chk':self.height_chk,
            'label':self.label,
            'tot_qty':self.tot_qty,
            'dimension_method':self.dimension_method,
            'custom_weight':self.custom_weight,
        })
        return res
