# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_sale_product_history_line_ids = fields.Many2many(
        'sale.order.line',
        'custom_sale_order_line_history',
        'custom_order_line_id',
        'custom_history_line_id', 
        string='Sale Order Line History',
        copy=False
    )

    def action_compute_product_history(self):
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']
        for rec in self:
            domain = [('order_id.partner_id', 'child_of', rec.partner_id.ids),
                ('order_id.state', 'not in', ('draft', 'cancel')),
                ('product_id','=',rec.mapped('order_line.product_id.id')),
                ('order_id.id','!=',rec.id)]
            sale_order_line_ids = sale_order_line_obj.search((domain),order="id desc")
            rec.custom_sale_product_history_line_ids = [(6, 0, sale_order_line_ids.ids)]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
