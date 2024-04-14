# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_webshop_add_agent = fields.Boolean(
        string='Added Agent',
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
