# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    custom_last_unit_price = fields.Float(
        'Previous Order Price', 
        required=False, 
        digits=dp.get_precision('Product Price'),
        copy=False 
    )
    custom_date_order = fields.Datetime(
        string='Order Date',
        related='order_id.date_order',
        readonly=True,
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        order_line_ids = self.env['purchase.order.line'].search([
            ('product_id','=',self.product_id.id),
            ('state','not in',('draft','cancel')),
            ('currency_id','=',self.order_id.currency_id.id)
            ], limit=1,order="custom_date_order desc,id desc")
        self.custom_last_unit_price = order_line_ids.price_unit
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: