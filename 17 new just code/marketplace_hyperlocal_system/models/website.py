# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################


from odoo import api, fields, models, _
from odoo.http import request
import requests
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    enable_hyperlocal = fields.Boolean(string="Enable")
    distance = fields.Float("Distance")
    def_address = fields.Char("Set Default Address")
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")

    def get_google_map_api_key(self):
        apikey = request.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
        return apikey if apikey else None 
