# See LICENSE file for full copyright and licensing details.

from ...woocommerce_api_client import WOOCOMMERCE
from odoo import models, fields


class ProductEcommerceField(models.Model):
    _inherit = 'product.ecommerce.field'

    type_api = fields.Selection(
        selection_add=[(WOOCOMMERCE, 'WooCommerce')],
        ondelete={
            WOOCOMMERCE: 'cascade',
        },
    )
