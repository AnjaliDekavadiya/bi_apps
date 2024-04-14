# See LICENSE file for full copyright and licensing details.

from .send_fields import SendFieldsWooCommerce
from odoo.addons.integration.models.fields import ProductProductSendMixin


class SendFieldsProductProductWooCommerce(SendFieldsWooCommerce, ProductProductSendMixin):

    def send_lst_price(self, field_name):
        return {
            field_name: str(self.get_price_by_send_tax_incl(self.odoo_obj.lst_price)),
        }

    def send_weight(self, field_name):
        weight_uom = self.adapter.get_weight_uom_for_converter()
        weight = self.convert_weight_uom_from_odoo(self.odoo_obj.weight, weight_uom)
        return {
            field_name: str(weight),
        }

    def send_allow_backorders(self, field_name):
        allow_backorders = self.odoo_obj.allow_backorders_on_product

        if allow_backorders == 'from_template':
            allow_backorders = self.odoo_obj.product_tmpl_id.allow_backorders_on_template

        return {
            field_name: allow_backorders,
        }
