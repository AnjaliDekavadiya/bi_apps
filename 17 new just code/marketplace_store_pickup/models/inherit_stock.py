# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from lxml import etree
import logging
_logger = logging.getLogger(__name__)


class MarketplaceStock(models.Model):
    _inherit = "marketplace.stock"

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context

        res = super(MarketplaceStock, self).fields_view_get(
            view_id, view_type, toolbar, submenu)
        doc = etree.XML(res['arch'])

        if context.get('active_model') == 'product.template':
            product_id = self.env['product.template'].browse(self._context.get('active_id'))
        else:
            product_obj = self.env['product.product'].search([('id', '=', self._context.get('active_id'))])
            product_id = product_obj.product_tmpl_id
        if product_id:
            product_obj = product_id.product_variant_ids[0]
            location_ids = product_id.seller_shop_ids.mapped('shop_location_id')
            location_ids = location_ids.ids if location_ids else []

            if product_obj.location_id:
                location_ids.append(product_obj.location_id.id)
            else:
                location_ids.append(product_obj.marketplace_seller_id.location_id.id)
            if location_ids:
                domain = "[('id','in'," + str(location_ids) +")]"
                for node in doc.xpath("//field[@name='location_id']"):
                    node.set('domain', domain)
        res['arch'] = etree.tostring(doc)
        return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    # def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        sol = values.get('sale_line_id',False)
        if sol:
            sol_obj = self.env["sale.order.line"].sudo().browse(int(sol))
            if sol_obj.store_id:
                if sol_obj.store_id.shop_location_id:
                    res["location_id"] = sol_obj.store_id.shop_location_id.id
                else:
                    res["location_id"] = sol_obj.store_id.seller_id.get_seller_global_fields('location_id')
        return res
