# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api,models, fields

class ProductTemplateinherit(models.Model):
    _inherit = 'product.template'

    sh_arabic_name = fields.Char(string='Custom Name', related='product_variant_ids.sh_arabic_name', readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplateinherit, self).create(vals_list)
        for vals in vals_list:
            if vals.get("sh_arabic_name", False):
                tags = vals.get("sh_arabic_name")
                if res and res.product_variant_id:
                    res.product_variant_id.sh_arabic_name = tags
        return res
