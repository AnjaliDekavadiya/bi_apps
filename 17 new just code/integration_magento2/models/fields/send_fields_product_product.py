# See LICENSE file for full copyright and licensing details.

from odoo.addons.integration.models.fields import ProductProductSendMixin

from .send_fields import SendFieldsMagento
from ...magento2_api_client import STATUS_ENABLED, STATUS_DISABLED


class SendFieldsProductProductMagento(SendFieldsMagento, ProductProductSendMixin):

    def convert_to_external(self):
        """
        Add the `reference` property for creating template `sku` on the fly based on its variants.
        """
        res = super().convert_to_external()

        ref_field = self.integration._get_product_reference_name()
        res['reference'] = getattr(self.odoo_obj, ref_field)

        return res

    def send_integration_name(self, field_name):
        return {
            field_name: self.convert_translated_field_to_integration_format('display_name'),
        }

    def send_lst_price(self, field_name):
        return {
            field_name: self.get_price_by_send_tax_incl(self.odoo_obj.lst_price),
        }

    def send_status(self, field_name):
        if self.integration.send_inactive_product and not self.external_id:
            return {field_name: STATUS_DISABLED}

        status = self.odoo_obj.active and self.odoo_obj.sale_ok

        return {
            field_name: status and STATUS_ENABLED or STATUS_DISABLED,
        }

    def send_integration_cost_price(self, field_name):
        cost = self.odoo_obj.standard_price
        if isinstance(cost, float):
            return {
                field_name: cost,
            }
        return {}
