# See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import _
from odoo.exceptions import UserError
from odoo.addons.integration.tools import IS_FALSE
from odoo.addons.integration.exceptions import NotMappedFromExternal
from odoo.addons.integration.models.fields import ProductTemplateReceiveMixin

from .receive_fields import ReceiveFieldsMagento
from ...magento2_api_client import NON_TAX_CLASS, STATUS_ENABLED, CUSTOM_ATTRIBUTES
from ...magento2.exceptions import Magento2ApiException


class ReceiveFieldsProductTemplateMagento(ReceiveFieldsMagento, ProductTemplateReceiveMixin):

    def __init__(self, integration, odoo_obj=False, external_obj=False):
        super().__init__(integration, odoo_obj, external_obj)

        if external_obj:
            self.product = self.external_obj['product']
            self.tmpl_attribute_value_ids = self.external_obj['tmpl_attribute_value_ids']
            self.custom_attributes = self.external_obj[CUSTOM_ATTRIBUTES]
            self.lang_versions = self.external_obj['lang_versions']

        if not self.odoo_obj:
            self.odoo_obj = self.env['product.template']

    def get_ext_attr(self, ext_attr_name):
        if ext_attr_name == 'attr_values_ids_by_attr_id':
            return self.find_attributes_in_odoo(self.tmpl_attribute_value_ids)

        raise UserError(_('Import attribute "%s" do not exist') % ext_attr_name)

    def find_attributes_in_odoo(self, ext_attribute_value_ids):
        ProductAttributeValue = self.env['product.attribute.value']
        result = defaultdict(list)

        for external_id in ext_attribute_value_ids:
            try:
                record = ProductAttributeValue.from_external(self.integration, external_id)
            except NotMappedFromExternal as ex:
                is_exists = self.integration.adapter._attribute_value_check_existing(external_id)
                if not is_exists:
                    raise Magento2ApiException(_(
                        'Attribute-Value ID "%s" does not exist in external system.' % external_id
                    ))
                raise ex

            attribute_id = record.attribute_id.id
            result[attribute_id].append(record.id)

        return result

    def _get_value(self, field_name):
        return self._get_ext_obj_value(self.product, field_name)

    def convert_from_external(self):
        result = self.calculate_receive_fields()

        # 'type' field should be set only during the initial import
        # (to avoid issues with 'type' field changes on products synchronisation -
        # Odoo doesn't allow to change existing products types)
        if not self.odoo_obj:
            result['type'] = self.adapter._convert_type_to_odoo(self.product['type_id'])

        return result

    def receive_integration_name(self, field_name):
        value = self._parse_langs(self.product, 'name', self.lang_versions, custom=False)
        name_value = self.convert_translated_field_to_odoo_format(value)
        odoo_field = self.odoo_obj.get_integration_name_field()
        return {
            odoo_field: name_value,
        }

    def receive_status(self, field_name):
        return {
            'sale_ok': self.product.get('status') == STATUS_ENABLED,
            field_name: self.product.get('status') == STATUS_ENABLED,
        }

    def receive_categories(self, field_name):
        ext_category_ids = self.custom_attributes.get('category_ids', [])

        return {
            field_name: [(6, 0, self.find_categories_in_odoo(ext_category_ids))],
        }

    def receive_list_price(self, field_name):
        if len(self.adapter._parse_product_variants(self.product)) > 1:
            return {field_name: 0}

        price = float(self._get_value('price') or 0)  # TODO price_including_taxes
        return {
            field_name: price,
        }

    def receive_taxes(self, field_name):
        id_tax_rules_group = self.custom_attributes.get('tax_class_id')
        if id_tax_rules_group in (NON_TAX_CLASS, IS_FALSE):
            id_tax_rules_group = False

        if id_tax_rules_group:
            odoo_tax = self._get_odoo_tax_from_external(id_tax_rules_group)
            tax_ids = [(6, 0, odoo_tax.ids)]
        else:
            tax_ids = [(5,)]

        return {
            field_name: tax_ids,
        }

    def receive_sku(self, field_name):
        return {
            field_name: self._get_value('sku'),
        }

    def receive_integration_cost_price(self, field_name):
        if not self.custom_attributes.get('cost'):
            return {}
        return {
            field_name: float(self.custom_attributes['cost'] or 0),
        }

    def receive_weight(self, field_name):
        weight_oum = self.adapter.store_weight_uom
        weight = self.product.get('weight')
        weight = self.convert_weight_uom_to_odoo(float(weight or 0), weight_oum)

        return {
            field_name: weight,
        }
