# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class ProductEcommerceFieldMapping(models.Model):
    _inherit = 'product.ecommerce.field.mapping'

    @api.onchange('send_on_update')
    def _onchange_send_on_update(self):
        """
        This method is added because there is no export implementation
        for the 'select' converter. Temporary restriction.
        """
        if self.ecommerce_field_id.value_converter == 'select':
            self.send_on_update = False
