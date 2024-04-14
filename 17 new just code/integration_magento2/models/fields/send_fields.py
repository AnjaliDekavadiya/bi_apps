# See LICENSE file for full copyright and licensing details.

from ...magento2_api_client import CUSTOM_ATTRIBUTES
from odoo.addons.integration.models.fields import SendFields
from odoo.addons.integration.models.fields.common_fields import (
    BOOLEAN_FIELDS,
)


class SendFieldsMagento(SendFields):

    def convert_translated_field_to_integration_format(self, field_name):
        language_mappings = self.env['integration.res.lang.mapping'].search([
            ('integration_id', '=', self.integration.id),
        ])

        translations = {}
        for language_mapping in language_mappings:
            external_code = language_mapping.external_language_id.code
            odoo_code = language_mapping.language_id.code
            translations[external_code] = getattr(
                self.odoo_obj.with_context(lang=odoo_code), field_name)

        return {'language': translations}

    def _update_calculated_fields(self, vals, field_values):
        for field_name, field_value in field_values.items():
            if field_name.startswith(f'{CUSTOM_ATTRIBUTES}.'):
                attribute_name = field_name.split('.')[-1]
                field_name = CUSTOM_ATTRIBUTES
                meta_value = {
                    'attribute_code': attribute_name,
                    'value': field_value,
                }
                field_value = vals.get(CUSTOM_ATTRIBUTES, []) + [meta_value]

            vals[field_name] = field_value

        return vals

    def send_weight(self, field_name):
        weight_uoms = self.adapter.get_shop_weight_uoms_for_converter()
        result = {
            store_code: self.convert_weight_uom_from_odoo(self.odoo_obj.weight, weight_uom)
            for store_code, weight_uom in weight_uoms.items()
        }

        return {
            field_name: result,
        }

    def _prepare_simple_value(self, field_name, field_type, odoo_value):
        if field_type in BOOLEAN_FIELDS:
            return int(odoo_value)

        return super()._prepare_simple_value(field_name, field_type, odoo_value)

    def _get_select_value(self, ecommerce_field):
        # The functionality for this method is not implemented yet.
        return {}
