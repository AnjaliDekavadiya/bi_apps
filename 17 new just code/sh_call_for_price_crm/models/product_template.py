# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    call_for_price = fields.Boolean("Call For Price ?")

    @api.model
    def _search_get_detail(self, website, order, options):
        result = super(ProductTemplate, self)._search_get_detail(
            website, order, options)
        result['fetch_fields'] = result['fetch_fields'] + ['call_for_price']

        mapping = {
            'call_for_price': {'name': 'call_for_price', 'type': 'boolean'},
        }
        result['mapping'].update(mapping)

        return result
