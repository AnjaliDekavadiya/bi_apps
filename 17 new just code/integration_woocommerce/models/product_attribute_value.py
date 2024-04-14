# See LICENSE file for full copyright and licensing details.

from odoo import models, _

from odoo.addons.integration.exceptions import NoExternal


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    def _find_external_by_name(self, integration, attribute_id, attribute_value_name):

        ExternalAttribute = self.env['integration.product.attribute.external']

        external_attr = ExternalAttribute.search([
            ('integration_id', '=', integration.id),
            ('code', '=', attribute_id),
        ], limit=1)

        if not external_attr:
            raise NoExternal(
                _('Cannot find external record'),
                ExternalAttribute._name,
                attribute_id,
                integration,
            )

        external_value = external_attr.external_attribute_value_ids\
            .filtered(lambda x: x.name == attribute_value_name)

        if not external_value:
            raise NoExternal(
                _('Cannot find external record by name'),
                external_value._name,
                f'{attribute_id}-<{attribute_value_name}>',
                integration,
            )

        return external_value
