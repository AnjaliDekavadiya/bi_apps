# See LICENSE file for full copyright and licensing details.

from odoo.addons.integration.models.fields import ReceiveFields

from ...woocommerce_api_client import WooCommerceApiClient, META_DATA


class ReceiveFieldsWooCommerce(ReceiveFields):

    def _get_value(self, field_name):
        if WooCommerceApiClient._is_metafield(field_name):
            key = self.adapter._truncate_name_by_dot(field_name)
            meta_data_dict = {x['key']: x['value'] for x in self.external_obj.get(META_DATA, [])}
            # Currently, if a user made a mistake in the meta-field definition
            # (for example, named it incorrectly), there should be no traceback, only a None value
            return meta_data_dict.get(key)

        return self.external_obj.get(field_name)
