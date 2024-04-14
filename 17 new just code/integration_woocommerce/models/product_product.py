# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    allow_backorders_on_product = fields.Selection(
        selection=[
            ('from_template', 'Use value from template'),
            ('no', 'Do not allow'),
            ('notify', 'Allow, but notify customer'),
            ('yes', 'Allow'),
        ],
        string='Allow Backorders',
        required=True,
        store=True,
        default='from_template',
        help='Define the backorder policy for this product. Select "Use value from template" '
             'to use the backorder setting from the product template, "Do not allow" to '
             'disallow backorders entirely, "Allow, but notify customer" to permit backorders '
             'with customer notification, and "Allow" to allow backorders without '
             'notification.',
    )
