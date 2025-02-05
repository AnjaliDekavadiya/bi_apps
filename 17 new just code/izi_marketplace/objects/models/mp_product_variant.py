# -*- coding: utf-8 -*-
# Copyright 2023 IZI PT Solusi Usaha Mudah

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class MarketplaceProductVariant(models.Model):
    _name = 'mp.product.variant'
    _inherit = 'mp.base'
    _description = 'Marketplace Product Variant'

    name = fields.Char(string="Product Variant Name", readonly=True)
    active = fields.Boolean(default=True)
    is_active = fields.Boolean()
    mp_product_id = fields.Many2one(comodel_name="mp.product", string="Marketplace Product", readonly=True, ondelete="cascade")
    currency_id = fields.Many2one(related="mp_account_id.currency_id")
    company_id = fields.Many2one(related="mp_account_id.company_id")
    default_code = fields.Char(string="Internal Reference")
    list_price = fields.Float(string="Sales Price", default=1.0, digits='Product Price',
                              help="Base price to compute the customer price. Sometimes called the catalog price.")
    weight = fields.Float(string="Weight", digits='Stock Weight',
                          help="The weight of the contents in Kg, not including any packaging, etc.")
    volume = fields.Float("Volume", help="The volume in m3.")
    image = fields.Binary(string="Image", attachment=True,
                          help="This field holds the image used as image for the product, limited to 1024x1024px.")
    image_medium = fields.Binary(string="Medium-sized image", attachment=True,
                                 help="Medium-sized image of the product. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved, "
                                      "only when the image exceeds one of those sizes. Use this field in form views "
                                      "or some kanban views.")
    image_small = fields.Binary(string="Small-sized image", attachment=True,
                                help="Small-sized image of the product. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")
    mp_product_variant_main_image_url = fields.Char(string="Marketplace Product Variant Main Image URL")

    stock = fields.Integer(string='Stock', readonly=True)


    # @api.multi
    def get_product(self):
        mp_map_product_line_obj = self.env['mp.map.product.line']
        map_line = mp_map_product_line_obj.search([
            ('mp_account_id', 'in', self.mapped('mp_account_id').ids),
            ('mp_product_variant_id', 'in', self.ids)
        ])
        return map_line.mapped('product_id')

    # @api.multi
    def _prepare_product_values(self):
        product_obj = self.env['product.product']

        self.ensure_one()
        values = {}

        # Get default values
        fields_with_default = []
        for fname, field in product_obj._fields.items():
            if field.default and field.store:
                fields_with_default.append(fname)
        values.update(product_obj.default_get(fields_with_default))

        # Set values from mp_product_variant
        mp_product_variant_data = self.copy_data()[0]
        fields_list = ['default_code', 'weight', 'volume']
        values.update(dict([(fname, mp_product_variant_data.get(fname)) for fname in fields_list]))

        if self._context.get('set_values'):
            values.update(self._context.get('set_values'))

        return values

    # @api.multi
    def create_product(self, product_tmpl):
        _logger = self.env['mp.base']._logger
        product_obj = self.env['product.product']

        self.ensure_one()

        values = self._prepare_product_values()
        values.update({'product_tmpl_id': product_tmpl.id})

        _log_msg = 'Creating product.product of "%s"' % self.name
        if self._context.get('_log_counter'):
            _log_msg = '%s %s' % (self._context.get('_log_counter'), _log_msg)
        _logger(self.marketplace, _log_msg)
        product = product_obj.create(values)
        return product
    
    def action_update_mp_product(self):
        return self.get_product().set_mp_data()
