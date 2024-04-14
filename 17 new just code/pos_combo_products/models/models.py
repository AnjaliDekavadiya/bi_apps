# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
import json
from functools import partial
import ast
from itertools import groupby

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_combo_product = fields.Boolean(string=" Is Combo Product", help="Enables combo feature for this product.")
    hide_product_price = fields.Boolean(string="Hide Product Price", help="Enable to hide product price for this product.",default="False")
    pos_combo_groups_ids = fields.Many2many('combo.groups',string="Combo Groups",help="Select categories you want to add to this product.")
     
class ComboGroups(models.Model):
    _name = 'combo.groups'

    name = fields.Char(string="Name")
    maximum_combo_products = fields.Integer("Maximum Combo Options",default=1 ,help="Maximum number of options that can be chosen from this category")
    minimum_combo_products = fields.Integer("Minimum Combo Options",default=0,help="Minimum number of options that can be chosen from this category.")
    combo_products_ids = fields.Many2many('combo.products',string="Category Options", help="Select options of your choice for this category.",required=True)

    @api.constrains('maximum_combo_products','minimum_combo_products','combo_products_ids')
    def validate_min_max_combo_products(self):
        """
        Raises validation errors based on necessary condition
        """
        if self.maximum_combo_products < 0 or self.minimum_combo_products < 0:
            raise ValidationError("Number of combo products cannot be negative.")
        if self.minimum_combo_products > self.maximum_combo_products:
            raise ValidationError("Minimum value cannot be greater than maximum value for combo products.")
       
class ComboProducts(models.Model):
    
    _name = 'combo.products'

    name = fields.Char(string="Name",required=True)
    image = fields.Binary(string="Image")
    price = fields.Float(string="Price")
    manage_inventory = fields.Boolean(string="Manage Inventory",default=False)
    product_id = fields.Many2one('product.product' , string="Products")

class PosConfig(models.Model):
    _inherit = 'pos.config'

    combo_popup_view = fields.Selection(
        [('grid', 'Grid View'), ('list', 'List View')],
        'Status',required=True,readonly=True, copy=False, default='grid')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_combo_popup_view = fields.Selection(related='pos_config_id.combo_popup_view',readonly=False)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        models = super()._pos_ui_models_to_load()
        models_to_load = ["combo.products", "combo.groups","product.product"]
        for rec in models_to_load:
            if rec not in models:
                models.append(rec) 
        return models

    def _loader_params_combo_products(self):
        domain_list =[]
        model_fields = ['name', 'price','image','manage_inventory','product_id']
        return {'search_params': {'domain': domain_list, 'fields': model_fields}}
    
    def _get_pos_ui_combo_products(self, params):
        fields = self.env['combo.products'].search_read(**params['search_params'])
        return fields

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(["is_combo_product", "pos_combo_groups_ids","hide_product_price",'product_variant_ids','product_variant_count'])
        return result  

    def _loader_params_combo_groups(self):
        domain_list =[]
        model_fields = ['name', 'maximum_combo_products', 'minimum_combo_products','combo_products_ids']
        return {'search_params': {'domain': domain_list, 'fields': model_fields}}
    
    def _get_pos_ui_combo_groups(self, params):
        fields = self.env['combo.groups'].search_read(**params['search_params'])
        return fields


class StockPicking(models.Model):
    _inherit='stock.picking'

    def _prepare_stock_move_combo_vals(self, line, qty,product):
        """
        Params:
        line:line of combo product
        qty:int qty of product selected in combo product
        product:product selected in combo product 
        returns combo product data for picking
        """
        result = {
            'name': line.name,
            'product_uom': line.product_id.uom_id.id,
            'picking_id': self.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id':product.id,
            'product_uom_qty': qty,
            'state': 'draft',
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
        }
        return result

    def _create_move_from_pos_order_lines(self, lines):
        """
        core function override to create picking for lines in combo product
        """
        self.ensure_one()
        lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id), key=lambda l: l.product_id.id)
        move_vals = []
        for dummy, olines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*olines)
            move_vals.append(self._prepare_stock_move_vals(order_lines[0], order_lines))

        # picking code for combo products
        combo_lines = lines.filtered(lambda l: l.product_id.pos_combo_groups_ids and l.product_id.is_combo_product and l.qty_combo_dict)
        for line in combo_lines:
            cached_json = ast.literal_eval(line.qty_combo_dict)
            if line.product_id.pos_combo_groups_ids:
                for key,value in cached_json.items():
                    if key and value:         
                        inventory_product = self.env['product.product'].browse(int(key)) 
                        if inventory_product and inventory_product.type in ['product', 'consu']:
                            move_vals.append(self._prepare_stock_move_combo_vals(line,value,inventory_product ))
                        
        #code end
        moves = self.env['stock.move'].create(move_vals)
        confirmed_moves = moves._action_confirm()
        confirmed_moves._add_mls_related_to_order(lines, are_qties_done=True)

    
class PosOrder(models.Model):
    _inherit = 'pos.order'

    qty_combo_dict = fields.Text()
    qty_wk_combo_ids  = fields.Text("Products")
    qty_combo_list_name = fields.Text()

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders,draft)
        for order_id in order_ids:
            if order_id.get('id'):
                order = self.browse([order_id.get('id')])
                if order:
                    combo_prod_ids = []
                    cached_json = ast.literal_eval(order.qty_wk_combo_ids)
                    for prod_id in cached_json:
                        combo_prod_ids.append(prod_id[0])
                    order_json = ast.literal_eval(order.qty_combo_dict)
                    order_name_json = ast.literal_eval(order.qty_combo_list_name)
                    for product_id in combo_prod_ids:
                        product = self.env['product.product'].search([('id', '=', product_id)])  
                        product_exists_line = self.env['pos.order.line'].search([('product_id', '=', product_id),('order_id', '=', order.id)]) 
                        qty = int(order_json.get(str(product_id)))
                        if not product_exists_line and product:
                            line_data = {
                                    'full_product_name':order_name_json.get(str(product_id)),
                                    'product_id' : product.id,
                                    'qty':qty ,
                                    'order_id': order.id,
                                    'price_subtotal': 0,
                                    'price_subtotal_incl':0,
                                }
                            rec = self.env['pos.order.line'].create(line_data)
                        else:
                            product_exists_line.write({'qty' : product_exists_line.qty + qty})  
                        
        return order_ids

    @api.model
    def _order_fields(self,ui_order):
        res = super(PosOrder,self)._order_fields(ui_order)
        res.update({'qty_combo_dict':json.dumps(ui_order.get('qty_combo_dict',"")),})
        res.update({'qty_wk_combo_ids':json.dumps(ui_order.get('qty_wk_combo_ids',"")) })  
        res.update({'qty_combo_list_name':json.dumps(ui_order.get('qty_combo_list_name',"")) })  
        return res
    
    def _get_fields_for_order_line(self):
        fields = super(PosOrder, self)._get_fields_for_order_line()
        fields.extend([
            'sel_combo_prod','qty_combo_dict','temp_arr','grid_temp_arr','is_combo_product'
        ])
        return fields
    
    def _get_fields_for_draft_order(self):
        fields = super(PosOrder, self)._get_fields_for_draft_order()
        fields.extend([ 'qty_combo_dict','qty_wk_combo_ids','qty_combo_list_name'])
        return fields
    
    def _get_order_lines(self, orders):
        order_lines = self.env['pos.order.line'].search_read(
                domain = [('order_id', 'in', [to['id'] for to in orders])],
                fields = self._get_fields_for_order_line())
        if order_lines != []:
            self._get_pack_lot_lines(order_lines)
        extended_order_lines = []
        for order_line in order_lines:
            order_line['product_id'] = order_line['product_id'][0]
            order_line['server_id'] = order_line['id']
            order_line['sel_combo_prod'] = order_line['sel_combo_prod']
            order_line['qty_combo_dict'] = order_line['qty_combo_dict']
            order_line['temp_arr'] = order_line['temp_arr']
            order_line['grid_temp_arr'] = order_line['grid_temp_arr']
            order_line['is_combo_product'] = order_line['is_combo_product']
            del order_line['id']
            if not 'pack_lot_ids' in order_line:
                order_line['pack_lot_ids'] = []
            extended_order_lines.append([0, 0, order_line])
        for order_id, order_lines in groupby(extended_order_lines, key=lambda x:x[2]['order_id']):
            next(order for order in orders if order['id'] == order_id[0])['lines'] = list(order_lines)

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_combo_product = fields.Boolean("Combo Product")
    qty_combo_dict = fields.Text()
    sel_combo_prod = fields.Text()
    temp_arr = fields.Text()
    grid_temp_arr = fields.Text()

    def _export_for_ui(self, orderline):
        res = super(PosOrderLine, self)._export_for_ui(orderline)
        res['sel_combo_prod'] = orderline.sel_combo_prod
        res['grid_temp_arr'] = orderline.grid_temp_arr
        res['temp_arr'] = orderline.temp_arr
        res['is_combo_product'] = orderline.is_combo_product
        res['qty_combo_dict'] = orderline.qty_combo_dict
        return res

    @api.model
    def _order_line_fields(self, line, session_id=None):
        line_data = super(PosOrderLine, self)._order_line_fields(line, session_id=None)
        line_data[2].update(
            {
                'is_combo_product': line[2].get('is_combo_product', False),
                'qty_combo_dict':line[2].get('qty_combo_dict', ''),
            })
        return line_data
    
