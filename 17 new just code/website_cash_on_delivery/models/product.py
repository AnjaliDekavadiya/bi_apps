# coding: utf-8

from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.product'

    not_allow_cod = fields.Boolean(
        string='Not Allow Cash Delivery',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
