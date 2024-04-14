# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
from odoo.exceptions import ValidationError

from .fields.send_fields import SendFieldsMagento
from .fields.send_fields_product_product import SendFieldsProductProductMagento
from .fields.send_fields_product_template import SendFieldsProductTemplateMagento
from .fields.receive_fields import ReceiveFieldsMagento
from .fields.receive_fields_product_product import ReceiveFieldsProductProductMagento
from .fields.receive_fields_product_template import ReceiveFieldsProductTemplateMagento

from ..magento2_api_client import Magento2ApiClient, MAGENTO_TWO


class SaleIntegration(models.Model):
    _inherit = 'sale.integration'

    type_api = fields.Selection(
        selection_add=[(MAGENTO_TWO, 'Magento 2')],
        ondelete={
            MAGENTO_TWO: 'cascade',
        },
    )
    is_multi_source_inventory = fields.Boolean(
        string='Multi Source Inventory',
    )

    def is_magento_two(self):
        self.ensure_one()
        return self.type_api == MAGENTO_TWO

    def action_active(self):
        result = super(SaleIntegration, self).action_active()

        if self.is_magento_two():
            adapter = self._build_adapter()
            weight_uoms = {
                store['code']: store['weight_unit'] for store in adapter.stores_active()
            }
            self.set_settings_value('shop_weight_uoms', weight_uoms)

        return result

    def get_class(self):
        self.ensure_one()
        if self.is_magento_two():
            return Magento2ApiClient

        return super(SaleIntegration, self).get_class()

    def advanced_inventory(self):
        if self.is_magento_two():
            return self.is_multi_source_inventory
        return super(SaleIntegration, self).advanced_inventory()

    def _get_configuration_postfix(self):
        self.ensure_one()

        if self.is_magento_two():
            return 'magento'

        return super(SaleIntegration, self)._get_configuration_postfix()

    def convert_external_tax_to_odoo(self, tax_id):
        if not self.is_magento_two():
            return super(SaleIntegration, self).convert_external_tax_to_odoo(tax_id)

        assert_message = 'Mаgento 2 integration expected product `taxes_id` as a string.'
        assert isinstance(tax_id, str) is True, assert_message

        external_tax_group = self.env['integration.account.tax.group.external'].search([
            ('integration_id', '=', self.id),
            ('code', '=', tax_id),
        ], limit=1)

        external_tax = external_tax_group.default_external_tax_id

        if not external_tax:
            tax_name = external_tax_group.name or tax_id

            raise ValidationError(_(
                'It is not possible to import product into Odoo, because you haven\'t defined '
                'default External Tax for Tax Group "%s". Please,  click "Quick Configuration" '
                'button on your integration "%s" to define that mapping.'
            ) % (tax_name, self.name))

        odoo_tax = self.env['account.tax'].from_external(
            self,
            external_tax.code,
        )

        return odoo_tax

    def _get_error_webhook_message(self, error):
        if not self.is_magento_two():
            return super(SaleIntegration, self)._get_error_webhook_message(error)

        return _('Magento 2 Webhook Error: %s') % error.args[0]

    def init_send_field_converter(self, odoo_obj=False):
        if not self.is_magento_two():
            return super(SaleIntegration, self).init_send_field_converter(odoo_obj)

        if getattr(odoo_obj, '_name', '') == 'product.template':
            return SendFieldsProductTemplateMagento(self, odoo_obj)
        if getattr(odoo_obj, '_name', '') == 'product.product':
            return SendFieldsProductProductMagento(self, odoo_obj)
        return SendFieldsMagento(self, odoo_obj)

    def init_receive_field_converter(self, odoo_obj=False, external_obj=False):
        if not self.is_magento_two():
            return super(SaleIntegration, self).init_receive_field_converter(odoo_obj, external_obj)

        if getattr(odoo_obj, '_name', '') == 'product.template':
            return ReceiveFieldsProductTemplateMagento(self, odoo_obj, external_obj)
        if getattr(odoo_obj, '_name', '') == 'product.product':
            return ReceiveFieldsProductProductMagento(self, odoo_obj, external_obj)
        return ReceiveFieldsMagento(self, odoo_obj, external_obj)

    def import_stock_levels_integration(self, location_line):
        if not self.is_magento_two():
            return super(SaleIntegration, self).import_stock_levels_integration(location_line)

        external_ids = self.env['integration.product.product.external'].search([
            ('code', 'not in', [False, '']),
            ('integration_id', '=', self.id),
        ])
        location = location_line.erp_location_id
        for rec in external_ids:
            job_kwargs = self._job_kwargs_apply_stock_single(rec.code, location)
            job = rec.with_delay(**job_kwargs).get_stock_levels_one_magento(location_line)

            erp_product = rec.mapping_model.to_odoo(self, rec.code, raise_error=False)
            record = erp_product or rec
            record.with_context(default_integration_id=self.id).job_log(job)

        return True

    def _get_weight_integration_fields(self):
        if not self.is_magento_two():
            return super(SaleIntegration, self)._get_weight_integration_fields()

        return [
            'integration_magento2.magento2_ecommerce_field_template_weight',
            'integration_magento2.magento2_ecommerce_field_variant_weight',
        ]
