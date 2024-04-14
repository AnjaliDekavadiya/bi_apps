# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_sale_history_ids = fields.Many2many(
        'sale.order',
        'custom_sale_order_history',
        'custom_order_id',
        'custom_history_id', 
        string='Sale Order History',
        compute='_compute_sale_order_history',
        copy=False
    )

    @api.depends('partner_id')
    def _compute_sale_order_history(self):
        print('=------start-------')
        sale_order_obj = self.env['sale.order']
        for rec in self:
            domain = [('partner_id', 'child_of', rec.partner_id.ids),('state', 'not in', ('draft', 'cancel'))]
            try:
                if int(rec.id):
                    domain += [('id', '!=', rec.id)]
            except:
                pass
            sale_order_ids = sale_order_obj.search((domain),order="date_order desc, id desc", limit=10)
            print('+++++++++++++++++++++',sale_order_ids)
            rec.custom_sale_history_ids = [(6, 0, sale_order_ids.ids)]
            print('================',rec.custom_sale_history_ids)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
