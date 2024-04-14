# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_backorders_on_template = fields.Selection(
        selection=[
            ('no', 'Do not allow'),
            ('notify', 'Allow, but notify customer'),
            ('yes', 'Allow'),
        ],
        string='Allow Backorders',
        required=True,
        default='no',
        help='Specify the backorder policy for this product. This setting determines how '
             'backorders are managed when the product is out of stock. Before defining '
             'this policy, ensure that you have activated the necessary integration '
             'mapping. If the appropriate mapping is not enabled, the backorder policy '
             'you set here will not be applied.',
    )
