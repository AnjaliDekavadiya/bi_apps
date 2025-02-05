# -*- coding: utf-8 -*-
from odoo import fields, models, exceptions, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_zatca = fields.Boolean(related="company_id.is_zatca")
    code_type = fields.Char(string="Barcode Code Type",
                            help="it must be in UPC, GTIN, Customs HS Code and multiple other codes")
