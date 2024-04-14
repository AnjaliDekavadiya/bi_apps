# See LICENSE file for full copyright and licensing details.

from odoo import _
from odoo.exceptions import UserError
from odoo.addons.integration.models.fields import ProductProductReceiveMixin

from .receive_fields import ReceiveFieldsWooCommerce
from ...woocommerce_api_client import STATUS_PRIVATE, STATUS_PUBLISH, STATUS_DRAFT


class ReceiveFieldsProductProductWooCommerce(ReceiveFieldsWooCommerce, ProductProductReceiveMixin):
    def __init__(self, integration, odoo_obj=False, external_obj=False):
        super().__init__(integration, odoo_obj, external_obj)

        if external_obj:
            self.template = self.external_obj['template']
            self.variant = self.external_obj
            self.product_code = self.template['id']

        if not self.odoo_obj:
            self.odoo_obj = self.env['product.product']

    def get_ext_attr(self, ext_attr_name):
        if ext_attr_name == 'variant_id':
            return self.adapter._build_product_external_code(self.product_code, self.variant['id'])
        if ext_attr_name == 'attribute_value_ids':
            return self.adapter.parse_custom_attributes(self.external_obj)

        raise UserError(_('Import attribute "%s" do not exist') % ext_attr_name)

    def receive_lst_price(self, field_name):
        price = float(self.variant.get('regular_price') or 0)  # TODO price_including_taxes
        extra_price = price - (self.odoo_obj.lst_price - self.odoo_obj.variant_extra_price)
        return {
            field_name: extra_price,
        }

    def receive_status(self, field_name):
        status = self.external_obj['status']
        return {
            'sale_ok': status in (STATUS_PRIVATE, STATUS_PUBLISH),
            field_name: status != STATUS_DRAFT,
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
