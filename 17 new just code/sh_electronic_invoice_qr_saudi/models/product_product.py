# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class Productinherit(models.Model):
    _inherit = 'product.product'

    sh_arabic_name = fields.Char(string='Custom Name')
