# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class IntegrationSaleOrderFactory(models.AbstractModel):
    _inherit = 'integration.sale.order.factory'

    @api.model
    def _try_get_odoo_product(self, integration, line, **kw):
        if integration.is_magento_two():
            # Presense of odoo_variant_id attribute tells that we already know Odoo
            # product.product ID, so there is no need to try to search.
            if 'odoo_variant_id' in line:
                return self.env['product.product'].browse(line['odoo_variant_id'])

        return super(IntegrationSaleOrderFactory, self)\
            ._try_get_odoo_product(integration, line, **kw)
