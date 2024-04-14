# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.product'

    custom_buffer_pickup_time = fields.Float(
        string='Backup Start Time',
    )
    custom_buffer_drop_time = fields.Float(
        string='Backup End Time',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
