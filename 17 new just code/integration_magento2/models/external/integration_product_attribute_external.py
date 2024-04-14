# See LICENSE file for full copyright and licensing details.

from odoo import models


class IntegrationProductAttributeExternal(models.Model):
    _inherit = 'integration.product.attribute.external'

    def _get_mode_create_variant(self, ext_id, values):
        if not self.integration_id.is_magento_two():
            return super(IntegrationProductAttributeExternal, self)._get_mode_create_variant(
                ext_id, values)

        if self.integration_id.is_import_dynamic_attribute:
            return 'dynamic'

        if len(values) > 1:
            attribute_codes = self.integration_id.get_settings_value('attribute_codes')
            attribute_codes_dict = {f'{x[0]}-{x[1]}': int(x[2]) for x in attribute_codes}
            if attribute_codes_dict.get(ext_id) == 0:
                return 'no_variant'
        return 'always'
