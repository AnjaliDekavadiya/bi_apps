# See LICENSE file for full copyright and licensing details.

from odoo import _
from odoo.exceptions import UserError
from odoo.addons.integration.models.fields import ProductProductReceiveMixin

from .receive_fields import ReceiveFieldsMagento
from ...magento2_api_client import STATUS_ENABLED, CUSTOM_ATTRIBUTES


class ReceiveFieldsProductProductMagento(ReceiveFieldsMagento, ProductProductReceiveMixin):

    def __init__(self, integration, odoo_obj=False, external_obj=False):
        super().__init__(integration, odoo_obj, external_obj)

        if external_obj:
            self.variant = self.external_obj['variant']
            self.product_attribute_codes = self.external_obj['product_attribute_codes']
            self.product_code = self.external_obj['product_code']
            self.custom_attributes = self.external_obj[CUSTOM_ATTRIBUTES]

        if not self.odoo_obj:
            self.odoo_obj = self.env['product.product']

    def get_ext_attr(self, ext_attr_name):
        if ext_attr_name == 'variant_id':
            return self.adapter._build_product_external_code(
                self.product_code, self.variant['id'])
        if ext_attr_name == 'attribute_value_ids':
            return self.adapter._parse_attribute_values_by_codes(
                self.product_attribute_codes,
                self.custom_attributes,
            )

        raise UserError(_('Import attribute "%s" do not exist') % ext_attr_name)

    def _get_value(self, field_name):
        return self._get_ext_obj_value(self.variant, field_name)

    def receive_integration_name(self, field_name):
        return {}

    def receive_lst_price(self, field_name):
        price = float(self.variant.get('price') or 0)  # TODO price_including_taxes
        extra_price = price - (self.odoo_obj.lst_price - self.odoo_obj.variant_extra_price)
        return {
            field_name: extra_price,
        }

    def receive_status(self, field_name):
        return {
            'sale_ok': self.variant.get('status') == STATUS_ENABLED,
            field_name: self.variant.get('status') == STATUS_ENABLED,
        }

    def receive_integration_cost_price(self, field_name):
        custom_attributes = self.adapter._parse_custom_attributes(self.variant)
        if custom_attributes.get('cost'):
            return {
                field_name: float(custom_attributes['cost'] or 0),
            }
        return {}

    def receive_weight(self, field_name):
        weight_oum = self.adapter.store_weight_uom
        weight = self.variant.get('weight')
        weight = self.convert_weight_uom_to_odoo(float(weight or 0), weight_oum)

        return {
            field_name: weight,
        }
