# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sh_is_partial_pay_product = fields.Boolean('Partial Pay Product')
