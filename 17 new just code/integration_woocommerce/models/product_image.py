# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProductImage(models.Model):
    _inherit = 'product.image'

    woocommerce_id = fields.Integer(string='WooCommerce Id')

    @api.onchange('image_1920')
    def on_change_image(self):
        self.woocommerce_id = False
