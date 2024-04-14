# -*- coding: utf-8 -*-

from odoo import fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    existence_type_id = fields.Many2one('existence.type.sunat', string='Existence Type')