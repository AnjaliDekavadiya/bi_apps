# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

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
            warning = "You can only enter length between minimum " + str(self.product_id.height_min_3) + " to maximum " + str(self.product_id.height_max_3) + "feet"
            return {

                'warning': {'title': 'Error!', 'message': warning},
                'value': {
            
                    'pro_length': '',
                            }
            }
    
    @api.depends('product_id', 'product_qty', 'pro_width', 'pro_length', 'pro_height')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for record in self:
            if not (record.pro_width or record.pro_height or record.pro_length):
                tot_qty = 1.00
            else:
                tot_qty = record.pro_width * record.pro_height * record.pro_length

            record.update({
                'tot_qty' : tot_qty
            })


    pro_length = fields.Float('Length')
    pro_width = fields.Float('Width')
    pro_height = fields.Float('Height')
    label = fields.Char('Label')
    length_chk = fields.Boolean('Length Checkbox')
    width_chk = fields.Boolean('Length Checkbox')
    height_chk = fields.Boolean('height Checkbox')
    tot_qty = fields.Float(compute='_compute_amount', digits=dp.get_precision('Dim QTY'), string='Dim Qty', readonly=True, store=True)
    custom_weight = fields.Float(compute='_compute_amount', string='Weight Ea.', readonly=True, store=True)



class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.onchange('pro_width')
    def onchange_width(self):
        
        if self.pro_width < self.product_id.width_min_2 or self.pro_width > self.product_id.width_max_2:
            self.pro_width = ''
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
            
    
    @api.depends('product_id', 'product_qty', 'pro_width', 'pro_length', 'pro_height')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for record in self:
            if not (record.pro_width or record.pro_height or record.pro_length):
                tot_qty = 1.00
            else:
                tot_qty = record.pro_width * record.pro_height * record.pro_length
            weight = tot_qty * record.product_id.weight
            record.update({
                'tot_qty' : tot_qty,
                'custom_weight' : weight,
            })

    pro_length = fields.Float('Length')
    pro_width = fields.Float('Width')
    pro_height = fields.Float('Height')
    label = fields.Char('Label')
    length_chk = fields.Boolean('Length Checkbox')
    width_chk = fields.Boolean('Length Checkbox')
    height_chk = fields.Boolean('height Checkbox')
    tot_qty = fields.Float(compute='_compute_amount', digits=dp.get_precision('Dim QTY'), string='Dim Qty', readonly=True, store=True)
    dimension_method = fields.Selection([('l_w_h', 'LenghtxWidthxHeight'), ('w_h', 'WidthxHeight')], 'Dimention Method')
    custom_weight = fields.Float(compute='_compute_amount', string='Weight Ea.', readonly=True, store=True)

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """

        if not self.product_id:
            self.bom_id = False
        elif not self.bom_id or self.bom_id.product_tmpl_id != self.product_tmpl_id or (self.bom_id.product_id and self.bom_id.product_id != self.product_id):
            bom = self.env['mrp.bom']._bom_find(self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id, bom_type='normal')[self.product_id]
            if bom.type == 'normal':
                self.bom_id = bom.id
                self.product_qty = self.bom_id.product_qty
                self.product_uom_id = self.bom_id.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id
                self.length_chk = self.product_id.active_1
                self.width_chk = self.product_id.active_2
                self.height_chk = self.product_id.active_3
                return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}


    def _generate_raw_move(self, bom_line, line_data):
        quantity = line_data['qty']
        # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
        alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
        if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
            return self.env['stock.move']
        if bom_line.product_id.type not in ['product', 'consu']:
            return self.env['stock.move']
        if self.bom_id.routing_id and self.bom_id.routing_id.location_id:
            source_location = self.bom_id.routing_id.location_id
        else:
            source_location = self.location_src_id
        original_quantity = self.product_qty - self.qty_produced
        data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
            'pro_length':bom_line.pro_length,
            'pro_width':bom_line.pro_width,
            'pro_height':bom_line.pro_height,
            'length_chk':bom_line.length_chk,
            'width_chk':bom_line.width_chk,
            'height_chk':bom_line.height_chk,
            'tot_qty':bom_line.tot_qty,
            'label':bom_line.label,
        }
        return self.env['stock.move'].create(data)
