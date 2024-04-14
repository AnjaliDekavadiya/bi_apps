# See LICENSE file for full copyright and licensing details.

from odoo.addons.integration.models.fields import ProductTemplateSendMixin

from .send_fields import SendFieldsMagento
from ...magento2_api_client import STATUS_ENABLED, STATUS_DISABLED


class SendFieldsProductTemplateMagento(SendFieldsMagento, ProductTemplateSendMixin):

    def convert_to_external(self):
        """
        Force add the `name` key to generate unique magento2 `url_key` property.
        """
        res = super().convert_to_external()

        # Currently the `full_reference` needs only for magento configurable product.
        # TODO: It may be too long due to the multiple variants.
        reference = '%s-%s' % (self.odoo_obj.id, '-'.join(x['reference'] for x in res['products']))
        res.update(
            name=self.odoo_obj.display_name,
            full_reference=reference,
        )
        return res

    def convert_pricelists(self, *args, **kw):
        raise NotImplementedError

    def send_integration_name(self, field_name):
        return {
            field_name: self.odoo_obj.get_integration_name(self.integration),
        }

    def send_status(self, field_name):
        if self.integration.send_inactive_product and not self.external_id:
            return {field_name: STATUS_DISABLED}

        status = self.odoo_obj.active and self.odoo_obj.sale_ok

        return {
            field_name: status and STATUS_ENABLED or STATUS_DISABLED,
        }

    def send_categories(self, field_name):
        categories = self.odoo_obj.get_categories(self.integration)
        default_category = self.adapter.get_settings_value('default_product_category_id')
        if default_category:
            categories.insert(0, default_category)

        return {
            field_name: list(set(categories)),
        }

    def send_taxes(self, field_name):
        taxes = self.odoo_obj.get_taxes(self.integration)
        assert len(taxes) <= 1, 'multiple taxes are not supported'

        if taxes:
            return {
                field_name: taxes[0]['tax_group_id'],
            }

        return {}

    def send_list_price(self, field_name):
        return self.send_price(field_name)

    def send_sku(self, field_name):
        ref_field = self.integration._get_product_reference_name()
        sku = getattr(self.odoo_obj, ref_field)

        if not sku:
            return {}
        return {field_name: sku}

    def send_integration_cost_price(self, field_name):
        if self._check_combinations_not_exist(self.odoo_obj):
            cost = self.odoo_obj.standard_price
            if isinstance(cost, float):
                return {
                    field_name: cost,
                }
        return {}
