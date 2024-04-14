# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models
from datetime import datetime,timedelta
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class stockmove(models.Model):
    _inherit = "stock.move"

    pro_length = fields.Float('Length')
    pro_width = fields.Float('Width')
    pro_height = fields.Float('Height')
    label  = fields.Char('Label')
    length_chk = fields.Boolean('Length Checkbox')
    width_chk = fields.Boolean('Length Checkbox')
    height_chk = fields.Boolean('height Checkbox')
    tot_qty = fields.Float(digits=dp.get_precision('Dim QTY'), string='Dim Qty', readonly=True, store=True)
    dimension_method = fields.Selection(related='picking_id.dimension_method',string="Dimention Method")
    custom_weight = fields.Float(string='Weight Ea.', readonly=True, store=True)

    def _prepare_procurement_values(self):
        """ Prepare specific key for moves or other componenets that will be created from a procurement rule
        comming from a stock move. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        self.ensure_one()
        group_id = self.group_id or False
        if self.rule_id:
            if self.rule_id.group_propagation_option == 'fixed' and self.rule_id.group_id:
                group_id = self.rule_id.group_id
            elif self.rule_id.group_propagation_option == 'none':
                group_id = False
        return {
            'company_id': self.company_id,
            'date_planned': self.date,
            'move_dest_ids': self,
            'group_id': group_id,
            'route_ids': self.route_ids,
            'warehouse_id': self.warehouse_id or self.picking_id.picking_type_id.warehouse_id or self.picking_type_id.warehouse_id,
            'priority': self.priority,
            'pro_length':self.pro_length,
            'pro_width':self.pro_width,
            'pro_height':self.pro_height,
            'label':self.label,
            'length_chk' : self.length_chk,
            'width_chk' : self.width_chk,
            'height_chk' : self.height_chk,
            'tot_qty' : self.tot_qty,
            'width' : self.width,
            'height' :  self.height,
            'dimension_method' :  self.dimension_method,
            'custom_weight':self.custom_weight,
        }


class StockPicking(models.Model):
    _inherit ="stock.picking"

    dimension_method = fields.Selection(related='sale_id.dimension_method',string="Dimention Method")


class StockRuleDetail(models.Model):
    _inherit = 'stock.rule'

    pro_length = fields.Float('Length')
    pro_width = fields.Float('Width')
    pro_height = fields.Float('Height')
    label = fields.Char('Label')
    dimension_method = fields.Selection([('l_w_h', 'LenghtxWidthxHeight'), ('w_h', 'WidthxHeight')], 'Dimention Method')
    length_chk = fields.Boolean('Length Checkbox')
    width_chk = fields.Boolean('Length Checkbox')
    height_chk = fields.Boolean('height Checkbox')
    tot_qty = fields.Float(digits=dp.get_precision('Dim QTY'), string='Dim Qty', readonly=True, store=True)
    custom_weight = fields.Float(string='Weight Ea.', readonly=True, store=True)

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        
        result = super(StockRuleDetail, self)._get_stock_move_values(\
            product_id, product_qty, product_uom, location_id, name, origin, company_id, values)

        result.update({
            'pro_width':values.get('pro_width'),
            'pro_height':values.get('pro_height'),
            'pro_length':values.get('pro_length'),
            'length_chk':values.get('length_chk'),
            'width_chk':values.get('width_chk'),
            'height_chk':values.get('height_chk'),
            'label':values.get('label'),
            'tot_qty':values.get('tot_qty'),
            'width':values.get('width',0),
            'height':values.get('height',0),
            'dimension_method':values.get('dimension_method'),
            'custom_weight':values.get('custom_weight'),
            })
        
        return result

    def _update_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, line):
        result = super(StockRuleDetail, self)._update_purchase_order_line(product_id, product_qty, product_uom, company_id, values, line)
        result.update({
            'width':values.get('width'),
            'height':values.get('height'),
            'pro_width':values.get('pro_width'),
            'pro_height':values.get('pro_height'),
            'pro_length':values.get('pro_length'),
            'length_chk':values.get('length_chk'),
            'width_chk':values.get('width_chk'),
            'height_chk':values.get('height_chk'),
            'label':values.get('label'),
            'tot_qty':values.get('tot_qty'),
            'dimension_method':values.get('dimension_method'),
            'custom_weight':values.get('custom_weight'),
        })
        return result

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        result = super(StockRuleDetail, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, values, po)
        result.update({
            'pro_width':values.get('pro_width'),
            'pro_height':values.get('pro_height'),
            'pro_length':values.get('pro_length'),
            'length_chk':values.get('length_chk'),
            'width_chk':values.get('width_chk'),
            'height_chk':values.get('height_chk'),
            'label':values.get('label'),
            'tot_qty':values.get('tot_qty'),
            'width':values.get('width'),
            'height':values.get('height'),
            'dimension_method':values.get('dimension_method'),  
            'custom_weight':values.get('custom_weight'),
        })
        return result
   

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom):
        result = super(StockRuleDetail, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom)
        result.update({
            'pro_width':values.get('pro_width'),
            'pro_height':values.get('pro_height'),
            'pro_length':values.get('pro_length'),
            'length_chk':values.get('length_chk'),
            'width_chk':values.get('width_chk'),
            'height_chk':values.get('height_chk'),
            'label':values.get('label'),
            'tot_qty':values.get('tot_qty'),
            'width': values.get('width'),
            'height': values.get('height'),
            'dimension_method': values.get('dimension_method'),
            'custom_weight':values.get('custom_weight'),
        })
        return result