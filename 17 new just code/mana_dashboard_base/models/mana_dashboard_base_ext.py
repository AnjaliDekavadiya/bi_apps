# -*- coding: utf-8 -*-

from odoo import models, api, exceptions, fields, _, tools
from odoo.exceptions import ValidationError
from odoo.fields import Field
import logging

_logger = logging.getLogger(__name__)


class ManaBaseExtend(models.AbstractModel):
    """
    base extend
    """
    _inherit = "base"

    @api.model
    def _add_inherited_fields(self):
        """
        extend to add custom code
        """
        super(ManaBaseExtend, self)._add_inherited_fields()
        self._after_inherited_fields()

    @api.model
    def _add_field_ext(self, name, field):
        """ Add the given ``field`` under the given ``name`` in the class """
        self._add_field(name, field)

    @api.model
    def _after_inherited_fields(self):
        pass

    @api.model
    def _add_field(self, name, field):
        """ Add the given ``field`` under the given ``name`` in the class """
        cls = type(self)

        # Assert the name is an existing field in the model, or any model in the _inherits
        # or a custom field (starting by `x_`)
        is_class_field = any(
            isinstance(getattr(model, name, None), fields.Field)
            for model in [cls] + [self.env.registry[inherit] for inherit in cls._inherits]
        )

        # if not (is_class_field or self.env['ir.model.fields']._is_manual_name(name)):
        #     raise ValidationError(
        #         f"The field `{name}` is not defined in the `{cls._name}` Python class and does not start with 'x_'"
        #     )

        # Assert the attribute to assign is a Field
        if not isinstance(field, fields.Field):
            raise ValidationError("You can only add `fields.Field` objects to a model fields")

        if not isinstance(getattr(cls, name, field), Field):
            _logger.warning("In model %r, field %r overriding existing value", cls._name, name)
        setattr(cls, name, field)
        field._toplevel = True
        field.__set_name__(cls, name)
        # add field as an attribute and in cls._fields (for reflection)
        cls._fields[name] = field