# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    custom_purchase_history_ids = fields.Many2many(
        'purchase.order',
        'custom_purchase_order_history',
        'custom_purchase_order_id',
        'custom_purchase_history_id', 
        string='Purchase Order History',
        compute='_compute_purchase_order_history',
        copy=False
    )

    @api.depends('partner_id')
    def _compute_purchase_order_history(self):
        purchase_order_obj = self.env['purchase.order']
        for rec in self:
            domain = [('partner_id', 'child_of', rec.partner_id.ids),('state', 'in', ('purchase', 'done'))]
            try:
                if int(rec.id):
                    domain += [('id', '!=', rec.id)]
            except:
                pass
            purchase_order_ids = purchase_order_obj.search((domain),order="date_order desc, id desc", limit=10)
            rec.custom_purchase_history_ids = [(6, 0, purchase_order_ids.ids)]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
