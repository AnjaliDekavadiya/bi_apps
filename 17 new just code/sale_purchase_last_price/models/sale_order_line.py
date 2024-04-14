# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class sale_order_line(models.Model):
    _inherit='sale.order.line'

    custom_last_unit_price = fields.Float(
        'Previous Order Price', 
        required=False, 
        digits=dp.get_precision('Product Price'), 
        default=0.0,
        copy=False
    )
    custom_date_order = fields.Datetime(
        string='Order Date',
        related='order_id.date_order',
        readonly=True,
    )

    # @api.multi
    @api.onchange('product_id')
    # def product_id_change(self):
    def product_id_change_custom(self):
        # res = super(sale_order_line, self).product_id_change()
        order_line_ids = self.env['sale.order.line'].sudo().search([
            ("product_id", "=", self.product_id.id),
            ("currency_id","=",self.order_id.currency_id.id),
            ('state','not in',('draft','cancel'))]
            ,limit=1, order="custom_date_order,id desc")
        self.custom_last_unit_price = order_line_ids.price_unit
        # return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: