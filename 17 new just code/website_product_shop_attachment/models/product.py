# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class product_template(models.Model):
    _inherit = "product.template"

    website_product_attachment = fields.Many2many(
        'ir.attachment',
        copy=True,
        help="Select attachment/documents which will be show on website shop on product page.",
        string="Website Attachments")
