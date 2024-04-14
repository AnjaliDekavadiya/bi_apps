# -*- coding: utf-8 -*

from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    is_laundry = fields.Boolean(
        string="Is Laundry"
    )
