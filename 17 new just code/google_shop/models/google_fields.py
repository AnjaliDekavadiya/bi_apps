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


class Detail_oauth2(models.Model):
    _name = 'google.fields'
    _description = 'Google fields for mapping'
    name = fields.Char(string="Field", required=True)
    required = fields.Boolean(string="Required")
