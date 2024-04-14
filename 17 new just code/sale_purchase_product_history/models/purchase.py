# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    custom_purchase_product_history_line_ids = fields.Many2many(
        'purchase.order.line',
        'custom_purchase_order_line_history',
        'custom_purchase_order_line_id',
        'custom_purchase_history_line_id', 
        string='Purchase Order Line History',
        copy=False
    )

    def action_compute_product_history(self):
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']
        for rec in self:
            domain = [('order_id.partner_id', 'child_of', rec.partner_id.ids),
                ('order_id.state', 'not in', ('draft', 'cancel')),
                ('product_id','=',rec.mapped('order_line.product_id.id')),
                ('order_id.id','!=',rec.id)]
            purchase_order_line_ids = purchase_order_line_obj.search((domain),order="id desc")
            rec.custom_purchase_product_history_line_ids = [(6, 0, purchase_order_line_ids.ids)]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
