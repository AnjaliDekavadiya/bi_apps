# See LICENSE file for full copyright and licensing details.

from odoo import _
from odoo.exceptions import ValidationError
from odoo.addons.integration.models.fields import ReceiveFields

from ...magento2_api_client import Magento2ApiClient


class ReceiveFieldsMagento(ReceiveFields):

    def _get_ext_obj_value(self, obj, field_name):
        return Magento2ApiClient._parse_ecommerce_value(obj, field_name)

    def _get_select_value(self, ecommerce_field):
        """
        Get the selected value for a specific ecommerce field.

        Args:
            ecommerce_field (EcommerceField): The ecommerce field object.

        Returns:
            dict: A dictionary containing the selected value as per the ecommerce field.
                If no valid value is found, it returns a dictionary with the field name and `False`.
        """
        field_name = ecommerce_field.odoo_field_id.name
        attribute_name = self.adapter._truncate_name_by_dot(ecommerce_field.technical_name)

        # Search for the corresponding external attribute
        external_attribute = self.env['integration.product.attribute.external'].search([
            ('code', 'like', f'%-{attribute_name}'),
            ('integration_id', '=', self.integration.id),
        ], limit=1)
        if not external_attribute:
            raise ValidationError(_(
                'Unable to find attribute "%s". Perform an Initial Import or check if the '
                'attribute name is correct') % (attribute_name,))

        # Get the external attribute ID from custom_attributes
        ext_attribute_value_id = self.custom_attributes.get(attribute_name, False)
        if not ext_attribute_value_id:
            return {field_name: self._prepare_simple_value(ecommerce_field, False)}

        ext_attribute_id, __ = self.adapter._parse_attribute_external_code(external_attribute.code)
        ext_attribute_value_code = self.adapter._build_attribute_value_external_code(
            ext_attribute_id, ext_attribute_value_id)

        # Get the external attribute value by its code
        ExtAttributeValue = self.env['integration.product.attribute.value.external']
        ext_attribute_value = ExtAttributeValue.get_external_by_code(
            self.integration,
            ext_attribute_value_code,
            raise_error=True,
        )

        return {field_name:  self._prepare_simple_value(
            ecommerce_field, ext_attribute_value.name)}
