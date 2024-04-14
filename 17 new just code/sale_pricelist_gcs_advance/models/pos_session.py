# -*- coding: utf-8 -*-
from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].extend(['product_brand_gcs'])
        return result

    def _product_pricelist_item_fields(self):
        res = super(PosSession, self)._product_pricelist_item_fields()
        custom_fields = ['product_brand', 'categ_product_brand', 'categ_brand_id']
        res += custom_fields
        return res
