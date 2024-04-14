#  See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
from odoo.exceptions import ValidationError, UserError

from .fields.send_fields import SendFields
from .fields.send_fields_product_product import SendFieldsProductProductWooCommerce
from .fields.send_fields_product_template import SendFieldsProductTemplateWooCommerce
from .fields.receive_fields import ReceiveFields
from .fields.receive_fields_product_product import ReceiveFieldsProductProductWooCommerce
from .fields.receive_fields_product_template import ReceiveFieldsProductTemplateWooCommerce

from ..woocommerce_api_client import WooCommerceApiClient, WOOCOMMERCE, WEIGHT_UOM


class SaleIntegration(models.Model):
    _inherit = 'sale.integration'

    type_api = fields.Selection(
        selection_add=[(WOOCOMMERCE, 'WooCommerce')],
        ondelete={
            WOOCOMMERCE: 'cascade',
        },
    )

    tracking_number_api_field_name = fields.Char(
        string='Tracking Number API Field Name'
    )

    fee_line_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Fee Line Product',
        domain="[('type', '=', 'service')]",
    )

    woocommerce_vat_metafield_field_name = fields.Char(
        string='WooCommerce VAT Metafield Name',
        default='_billing_eu_vat_number',
    )

    set_customer_language_based_on_orders_metadata = fields.Boolean(
        string='Set Customer Language based on language from orders metadata',
        default=True,
    )

    def is_woocommerce(self):
        self.ensure_one()
        return self.type_api == WOOCOMMERCE

    def get_class(self):
        self.ensure_one()
        if self.is_woocommerce():
            return WooCommerceApiClient

        return super(SaleIntegration, self).get_class()

    def action_active(self):
        result = super(SaleIntegration, self).action_active()

        if self.is_woocommerce():
            adapter = self._build_adapter()
            wc_option = adapter.get(WEIGHT_UOM)  # TODO: what a hell this action doing here

            if wc_option:
                self.set_settings_value('weight_uom', wc_option[0]['value'])

        return result

    def fill_image_mapping(self, image_mapping_dict):
        if not self.is_woocommerce():
            return super().fill_image_mapping(image_mapping_dict)

        MappingAny = self.env['integration.mapping.any']

        for image_mappings in image_mapping_dict.values():
            for image_mapping in image_mappings:
                MappingAny.update_mapping_any(
                    integration=self,
                    odoo_obj_name=image_mapping['odoo_obj_name'],
                    odoo_obj_id=image_mapping['odoo_obj_id'],
                    odoo_obj_field_name=image_mapping['odoo_obj_field_name'],
                    external_obj_name='image',
                    external_obj_id=image_mapping['external_image_id']
                )

    def _retrieve_webhook_routes(self):
        if self.is_woocommerce():
            routes = {
                'orders': [
                    ('Order Created', 'order.created'),
                    ('Order Updated', 'order.updated'),
                ],
            }
            return routes
        return super(SaleIntegration, self)._retrieve_webhook_routes()

    def _get_error_webhook_message(self, error):
        if not self.is_woocommerce():
            return super(SaleIntegration, self)._get_error_webhook_message(error)

        return _('WooCommerce Webhook Error: %s') % error.args[0]

    def convert_external_tax_to_odoo(self, tax_class_id):
        if not self.is_woocommerce():
            return super(SaleIntegration, self).convert_external_tax_to_odoo(tax_class_id)

        assert_message = 'WooCommerce integration expected product `tax_class` as a string.'
        assert isinstance(tax_class_id, str) is True, assert_message

        external_tax_group = self.env['integration.account.tax.group.external'].search([
            ('integration_id', '=', self.id),
            ('code', '=', tax_class_id),
        ], limit=1)

        external_tax = external_tax_group.default_external_tax_id

        if not external_tax:
            tax_name = external_tax_group.name or tax_class_id

            raise ValidationError(_(
                'It is not possible to import product into Odoo, because you haven\'t defined '
                'default External Tax for Tax Group "%s". Please,  click "Quick Configuration" '
                'button on your integration "%s" to define that mapping.'
            ) % (tax_name, self.name))

        odoo_tax = self.env['account.tax'].from_external(
            self,
            external_tax.code,
        )

        return odoo_tax

    def init_send_field_converter(self, odoo_obj=False):
        if not self.is_woocommerce():
            return super(SaleIntegration, self).init_send_field_converter(odoo_obj)

        if getattr(odoo_obj, '_name', '') == 'product.template':
            return SendFieldsProductTemplateWooCommerce(self, odoo_obj)
        if getattr(odoo_obj, '_name', '') == 'product.product':
            return SendFieldsProductProductWooCommerce(self, odoo_obj)
        return SendFields(self, odoo_obj)

    def init_receive_field_converter(self, odoo_obj=False, external_obj=False):
        if not self.is_woocommerce():
            return super(SaleIntegration, self).init_receive_field_converter(odoo_obj, external_obj)

        if getattr(odoo_obj, '_name', '') == 'product.template':
            return ReceiveFieldsProductTemplateWooCommerce(self, odoo_obj, external_obj)
        if getattr(odoo_obj, '_name', '') == 'product.product':
            return ReceiveFieldsProductProductWooCommerce(self, odoo_obj, external_obj)
        return ReceiveFields(self, odoo_obj, external_obj)

    def import_stock_levels_integration_woocommerce(self, external_ids, location_line):
        assert self.is_woocommerce()
        location_id = location_line.erp_location_id
        external_location_code = location_line.external_location_id.code

        adapter = self.adapter
        stock_levels_data = adapter.get_stock_level_by_codes(external_ids, external_location_code)
        stock_levels = [(key, value) for key, value in stock_levels_data.items()]
        return self.run_apply_stock_levels_by_blocks(stock_levels, location_id)

    def _get_weight_integration_fields(self):
        if not self.is_woocommerce():
            return super(SaleIntegration, self)._get_weight_integration_fields()

        return [
            'integration_woocommerce.woocommerce_ecommerce_field_template_weight',
            'integration_woocommerce.woocommerce_ecommerce_field_variant_weight',
        ]

    def export_tracking(self, pickings):
        if self and self.is_woocommerce():
            if not self.tracking_number_api_field_name:
                raise UserError(_(
                    '"Tracking Number API Field Name" not specified for the "%s" integration '
                    'on "Sale Order Defaults" tab.' % self.name
                ))

        return super(SaleIntegration, self).export_tracking(pickings)

    def _prepare_inventory_data(self, product, ext_product, ext_location_id):
        """
        Prepare inventory data for WooCommerce synchronization.

        :param product: The Odoo product record.
        :param ext_product: The external product.
        :param ext_location_id: List of location IDs for which inventory data is being prepared.
        :return: A list of dictionaries containing inventory data.
        """
        inventory_data = super(SaleIntegration, self)._prepare_inventory_data(
            product, ext_product, ext_location_id)

        qty = inventory_data['qty']

        inventory_data.update({
            'manage_stock': True,
            'stock_quantity': qty,
        })

        return inventory_data
