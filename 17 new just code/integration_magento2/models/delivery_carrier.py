# See LICENSE file for full copyright and licensing details.

from odoo import models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def get_external_carrier_code(self, integration):
        if integration.is_magento_two():
            external = self.to_external_record(integration, raise_error=False)
            return external.code

        return super(DeliveryCarrier, self).get_external_carrier_code(integration)
