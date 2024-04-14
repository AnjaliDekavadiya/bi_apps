# See LICENSE file for full copyright and licensing details.

from odoo.addons.integration.models.fields import SendFields
from odoo.addons.integration.models.fields.common_fields import FLOAT_FIELDS

from ...woocommerce_api_client import WooCommerceApiClient
from ...woocommerce_api_client import STATUS_PENDING, STATUS_PUBLISH, STATUS_DRAFT, META_DATA


class SendFieldsWooCommerce(SendFields):

    def convert_translated_field_to_integration_format(self, field_name):
        language_mappings = self.env['integration.res.lang.mapping'].search([
            ('language_id', '!=', False),
            ('integration_id', '=', self.integration.id),
        ])

        translations = dict()
        for mapping in language_mappings:
            external_code = mapping.external_language_id.code
            odoo_code = mapping.language_id.code

            translated_value = getattr(self.odoo_obj.with_context(lang=odoo_code), field_name)
            translations[external_code] = translated_value

        return dict(language=translations)

    def _prepare_simple_value(self, field_name, field_type, odoo_value):
        if field_type in FLOAT_FIELDS:
            return str(odoo_value)

        return super()._prepare_simple_value(field_name, field_type, odoo_value)

    def send_status(self, field_name):
        if self.integration.send_inactive_product and not self.external_id:
            return {field_name: STATUS_DRAFT}
        if self.odoo_obj.active and self.odoo_obj.sale_ok:
            return {field_name: STATUS_PUBLISH}
        if self.odoo_obj.active and not self.odoo_obj.sale_ok:
            return {field_name: STATUS_PENDING}
        return {field_name: STATUS_DRAFT}

    def _update_calculated_fields(self, vals, field_values):
        for field_name, field_value in field_values.items():

            if WooCommerceApiClient._is_metafield(field_name):
                key = self.adapter._truncate_name_by_dot(field_name)

                meta_value = dict(key=key, value=field_value)
                field_value = vals.pop(META_DATA, []) + [meta_value]
                field_name = META_DATA

            vals[field_name] = field_value

        return vals
