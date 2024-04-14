# See LICENSE file for full copyright and licensing details.

from odoo import _
from odoo.exceptions import UserError
from odoo.addons.integration.models.fields.common_fields import GENERAL_GROUP

from .receive_fields import ReceiveFieldsWooCommerce
from ...woocommerce_api_client import STATUS_PRIVATE, STATUS_PUBLISH, STATUS_DRAFT


class ReceiveFieldsProductTemplateWooCommerce(ReceiveFieldsWooCommerce):
    def __init__(self, integration, odoo_obj=False, external_obj=False):
        super().__init__(integration, odoo_obj, external_obj)

        if not self.odoo_obj:
            self.odoo_obj = self.env['product.template']

    def get_ext_attr(self, ext_attr_name):
        if ext_attr_name == 'attr_values_ids_by_attr_id':
            return self.find_attributes_in_odoo(
                self.adapter.parse_custom_attributes(self.external_obj))

        raise UserError(_('Import attribute "%s" do not exist') % ext_attr_name)

    def convert_from_external(self):
        result = self.calculate_receive_fields()

        # 'type' field should be set only during the initial import
        # (to avoid issues with 'type' field changes on products synchronisation -
        # Odoo doesn't allow to change existing products types)
        if not self.odoo_obj:
            result['type'] = self.adapter._convert_type_to_odoo(self.external_obj)

        return result

    def receive_integration_name(self, field_name):
        name_value = self.convert_translated_field_to_odoo_format(self.external_obj.get('name'))
        odoo_field = self.odoo_obj.get_integration_name_field()
        return {
            odoo_field: name_value,
        }

    def receive_price(self, field_name):
        price = float(self.external_obj['regular_price'] or 0)  # TODO price_including_taxes
        return {
            field_name: price,
        }

    def receive_status(self, field_name):
        status = self.external_obj['status']
        return {
            field_name: status != STATUS_DRAFT,
            'sale_ok': status in (STATUS_PRIVATE, STATUS_PUBLISH),
        }

    def receive_categories(self, field_name):
        external_categories = self.external_obj.get('categories')
        ext_category_ids = [x['id'] for x in external_categories]

        return {
            field_name: [(6, 0, self.find_categories_in_odoo(ext_category_ids))],
        }

    def receive_taxes(self, field_name):
        tax_class = self.external_obj['tax_class'] or 'standard'
        odoo_tax = self._get_odoo_tax_from_external(tax_class)
        return {
            field_name: [(6, 0, odoo_tax.ids)],
        }

    def receive_product_features(self, field_name):
        ProductFeatureValue = self.env['product.feature.value']
        odoo_features = [(5, 0)]

        feature = self.env['product.feature'].from_external(self.integration, GENERAL_GROUP)

        for feature_line in self.external_obj.get('tags', []):
            feature_value = ProductFeatureValue.from_external(self.integration, feature_line['id'])

            if feature and feature_value:
                odoo_features.append((0, 0, {
                    'feature_id': feature.id,
                    'feature_value_id': feature_value.id,
                }))

        return {
            field_name: odoo_features,
        }

    def receive_weight(self, field_name):
        weight_uom = self.adapter.get_weight_uom_for_converter()
        weight = self.convert_weight_uom_to_odoo(
            float(self.external_obj['weight'] or 0), weight_uom)

        return {
            field_name: weight,
        }

    def receive_allow_backorders(self, field_name):
        allow_backorders = self.external_obj.get('backorders')

        return {
            field_name: allow_backorders,
        }
