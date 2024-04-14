#  See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from ...magento2_api_client import MAGENTO_TWO


class ProductEcommerceField(models.Model):
    _inherit = 'product.ecommerce.field'

    type_api = fields.Selection(
        selection_add=[(MAGENTO_TWO, 'Magento 2')],
        ondelete={
            MAGENTO_TWO: 'cascade',
        },
    )

    value_converter = fields.Selection(
        selection_add=[('select', 'Select Field (only for Magento 2)')],
        ondelete={
            'select': 'cascade',
        },
    )

    @api.constrains('value_converter')
    def _check_value_converter(self):
        for record in self:
            if record.type_api != MAGENTO_TWO and record.value_converter == 'select':
                raise ValidationError(
                    _('The selected option is only for Magento 2 API.')
                )

    @api.onchange('value_converter', 'default_for_update')
    def _onchange_value_converter(self):
        """
        This method is added because there is no export implementation
        for the 'select' converter. Temporary restriction.
        """
        if self.value_converter == 'select':
            self.default_for_update = False
