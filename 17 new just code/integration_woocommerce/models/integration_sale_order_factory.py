# See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.addons.integration.exceptions import ApiImportError


class IntegrationSaleOrderFactory(models.AbstractModel):
    _inherit = 'integration.sale.order.factory'

    @api.model
    def _try_get_odoo_product(self, integration, line, **kw):
        if integration.is_woocommerce():
            # Presense of odoo_variant_id attribute tells that we already know Odoo
            # product.product ID, so there is no need to try to search.
            if 'odoo_variant_id' in line:
                return self.env['product.product'].browse(line['odoo_variant_id'])

        return super(IntegrationSaleOrderFactory, self)\
            ._try_get_odoo_product(integration, line, **kw)

    def _create_order_additional_lines(self, order, order_data):
        integration = order.integration_id

        if integration.is_woocommerce() and order_data.get('fee_data'):
            self._create_line_with_fee_product(order, order_data.get('fee_data'))

        return super(IntegrationSaleOrderFactory, self)\
            ._create_order_additional_lines(order, order_data)

    def _create_line_with_fee_product(self, order, fee_data):
        integration = order.integration_id

        if not integration.fee_line_product_id:
            raise ApiImportError(_(
                'Fee Line Product is empty. Please, feel it in '
                'Sale Integration on the tab "Sale Order Defaults".'
            ))

        created_lines = self.env['sale.order.line']
        vals_list = []

        for fee_line in fee_data:
            odoo_tax = False
            fee_price = fee_line['total']

            if fee_line['taxes']:
                tax_class = fee_line['tax_class'] or 'standard'
                odoo_tax = integration.convert_external_tax_to_odoo(tax_class)
                if self._get_tax_price_included(odoo_tax):
                    fee_price += fee_line['total_tax']

            vals = {
                'product_id': integration.fee_line_product_id.id,
                'order_id': order.id,
                'price_unit': fee_price,
                'tax_id': odoo_tax and odoo_tax.ids or False,
                'name': fee_line['name'],
            }

            vals_list.append(vals)

        if vals_list:
            created_lines = self.env['sale.order.line'].create(vals_list)

        return created_lines
