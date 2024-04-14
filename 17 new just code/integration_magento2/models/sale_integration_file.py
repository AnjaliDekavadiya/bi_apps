# See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleIntegrationInputFile(models.Model):
    _inherit = 'sale.integration.input.file'

    def _get_external_reference(self):
        if self.si_id.is_magento_two():
            return self._get_external_reference_root('increment_id')
        return super(SaleIntegrationInputFile, self)._get_external_reference()
