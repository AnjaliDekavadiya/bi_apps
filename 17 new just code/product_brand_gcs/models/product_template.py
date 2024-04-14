# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_brand_gcs = fields.Many2one("product.brand.gcs", string="Product Brand", help="Select product brand")
