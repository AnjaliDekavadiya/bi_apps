# -*- coding: utf-8 -*-
from odoo import models, _


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        """
        :note:
            categ_product_brand: Product Brand 2
            categ_brand_id: Product Category 2
        """
        res = super(Pricelist, self)._get_applicable_rules_domain(products=products, date=date, **kwargs)
        res.extend([
            '|', ('product_brand', '=', False), ('product_brand', 'in', products.product_brand_gcs.ids),
            '|', ('categ_product_brand', '=', False), ('categ_product_brand', 'in',
                                                       products.product_brand_gcs.ids),
            '|', ('categ_brand_id', '=', False), ('categ_brand_id', 'child_of', products.categ_id.ids),
        ])
        return res
