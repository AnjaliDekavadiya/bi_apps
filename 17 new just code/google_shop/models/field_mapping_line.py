# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>;)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
##########################################################################
from odoo.addons.http_routing.models.ir_http import slug
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class FieldMapping(models.Model):
    _name = 'field.mapping.line'
    _description = 'Odoo field mapping with Google fields'
    google_field_id = fields.Many2one(comodel_name='google.fields', string="Google Fields",
                                      help="Select the google field name that you want to map with Odoo field")
    fixed = fields.Boolean(string="Fixed", default=False,
                           help="Select wether you want to send the fixed data or the field data")
    model_field_id = fields.Many2one(
        comodel_name='ir.model.fields', domain="[('model','=','product.product'),('ttype','in',('char','boolean','text','float','integer','date','datetime','selection','many2one'))]")
    field_mapping_id = fields.Many2one(
        comodel_name='field.mapping', help="Field with which you want to map")
    fixed_text = fields.Char(
        string="Text", help="Fixed data that you want to send")
    default = fields.Char(
        string="Default", help="The data enter here will be send when there is no data in the field")
    is_a_attribute = fields.Boolean(string="Is a attribute", default=False)
    attribute_id = fields.Many2one('product.attribute','Attribute Field')
