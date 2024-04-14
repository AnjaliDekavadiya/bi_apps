# See LICENSE file for full copyright and licensing details.

from odoo import models, _

from ...magento2.exceptions import Magento2ApiException


class IntegrationProductProductExternal(models.Model):
    _inherit = 'integration.product.product.external'

    def get_stock_levels_one_magento(self, location_line):
        self.ensure_one()
        integration = self.integration_id
        assert integration.is_magento_two()

        product_code = self.code
        external_location_code = location_line.external_location_id.code

        adapter = integration._build_adapter()
        __, product_id = adapter._parse_product_external_code(product_code)
        stock_item = adapter.get_stock_levels_one(product_id, external_location_code)
        if not stock_item:
            raise Magento2ApiException(_('External product "%s" not found') % product_id)

        result = integration._integration_apply_stock_qty(
            location_line.erp_location_id,
            product_code,
            stock_item.get('qty'),
            delay=False,
        )
        return result
