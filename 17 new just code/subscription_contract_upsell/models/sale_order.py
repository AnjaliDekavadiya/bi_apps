# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    is_upsell_quotation = fields.Boolean(
        string="Is Upsell Quotation ?", 
        default=False,
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
