# See LICENSE file for full copyright and licensing details.

from odoo import _
from odoo.addons.integration.models.fields import ProductTemplateSendMixin

from .send_fields import SendFieldsWooCommerce
from ...woocommerce_api_client import ATTRIBUTE_VALUE


class SendFieldsProductTemplateWooCommerce(SendFieldsWooCommerce, ProductTemplateSendMixin):

    def convert_to_external(self):
        result = super(SendFieldsProductTemplateWooCommerce, self).convert_to_external()

        # 1. Parse attributes
        attributes = []
        # For Woo we have to generate list of attributes with the values names
        # [{
        #   'id': 1
        #   'variation': True
        #   'options': ['Black', 'Green', 'Red']
        # }..]
        valid_attribute_lines = self.odoo_obj.valid_product_template_attribute_line_ids.filtered(
            lambda x: not x.exclude_from_synchronization
        )
        for attr_line in valid_attribute_lines:
            wc_attr_id = attr_line.attribute_id.to_external_or_export(self.integration)

            values = []

            for value_id in attr_line.value_ids:
                wc_attr_value_id = value_id.to_external_or_export(self.integration)
                wc_attr_value = self.adapter.get(ATTRIBUTE_VALUE % (wc_attr_id, wc_attr_value_id))

                error_msg = _('Attribute value with id %s does not exist in attribute with id %s'
                              ' in WooCommerce') % (wc_attr_value_id, wc_attr_id)
                assert len(wc_attr_value) == 1, error_msg

                values.append(wc_attr_value[0]['name'])

            attributes.append({
                'id': int(wc_attr_id),
                'variation': True,
                'options': values,
            })

        result['attributes'] = attributes

        # 2. Parse mapped languages
        mapping_ids = self.odoo_obj.env['integration.res.lang.mapping'].search([
            ('language_id', '!=', False),
            ('integration_id', '=', self.integration.id),
        ])
        result['langs'] = mapping_ids.mapped('external_language_id.code')
        return result

    def convert_pricelists(self, *args, **kw):
        raise NotImplementedError

    def send_categories(self, field_name):
        categories_list = self.odoo_obj.get_categories(self.integration)

        return {
            field_name: [{'id': x} for x in set(categories_list)],
        }

    def send_taxes(self, field_name):
        taxes = self.odoo_obj.get_taxes(self.integration) or [{'tax_group_id': 'standard'}]

        return {
            field_name: taxes[0]['tax_group_id'],
        }

    def send_product_features(self, field_name):
        features = self.odoo_obj.get_product_features(self.integration)

        return {
            field_name: [{'id': x['id_feature_value']} for x in features],
        }

    def send_weight(self, field_name):
        weight_uom = self.adapter.get_weight_uom_for_converter()
        weight = self.convert_weight_uom_from_odoo(self.odoo_obj.weight, weight_uom)
        return {
            field_name: str(weight),
        }

    def send_allow_backorders(self, field_name):
        allow_backorders = self.odoo_obj.allow_backorders_on_template

        return {
            field_name: allow_backorders,
        }
