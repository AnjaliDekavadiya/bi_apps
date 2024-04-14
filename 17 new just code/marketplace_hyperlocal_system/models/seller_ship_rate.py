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


from odoo import models, fields, api, _
import math
from odoo.http import request
from odoo.exceptions import UserError
import math
import logging
_logger = logging.getLogger(__name__)
import requests
from werkzeug.urls import url_encode

class SellerShipRate(models.Model):
    _name = 'seller.ship.rate'
    _description = "Seller Ship Rate"

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    name = fields.Many2one("res.partner", string="Seller", default=_set_seller_id,
        copy=False, required=True)
    distance_from = fields.Float("Distance From")
    distance_to = fields.Float("Distance To")
    weight_from = fields.Float("Weight From")
    weight_to = fields.Float("Weight To")
    cost = fields.Float("Shipping Cost")

    def getDistance(self, location, customerLocation):
        distance = 0
        apikey = self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
        if not apikey:
            raise UserError(_(
                "API key for GeoCoding (Places) required.\n"
                "Visit https://developers.google.com/maps/documentation/geocoding/get-api-key for more information."
            ))
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        payload={
            'origins': ",".join(map(str,location)),
            'destinations': ",".join(map(str,customerLocation)),
            'key': apikey,
        }
        payload = url_encode(payload)
        try:
            response = requests.get(url, params=payload)
            data = response.json()
            rows = data['rows'][0] if data.get('rows') else None
            elements = rows['elements'][0] if rows and rows.get('elements') else None
            if elements:
                if elements.get('status') and elements['status'] == 'ZERO_RESULTS':
                    return -1
                distance = elements['distance']['value']
                radiusUnit = self.env['ir.default'].sudo()._get('res.config.settings', 'radius_unit')
                if radiusUnit == 'mile':
                    distance = distance / 1609
                else:
                    distance = distance / 1000

        except Exception as e:
            _logger.info("=========Exception===========%r===========",e)
        return distance

    def getdefaultLongLat(self):
        latitude = request.session.get('latitude')
        longitude = request.session.get('longitude')
        if not latitude:
            latitude = request.website.latitude
            longitude = request.website.longitude
            request.session['latitude'] = latitude
            request.session['longitude'] = longitude
            website_order = request.website.sale_get_order()
            if website_order:
                website_order.sudo().unlink()
        if latitude == 0.0 and longitude == 0.0:
            default_address = request.website.def_address
            if default_address:
                data = request.env['base.geocoder'].sudo().geo_find(default_address)
                if data:
                    latitude = data[0]
                    longitude = data[1]
                    request.session['latitude'] = latitude
                    request.session['longitude'] = longitude
                    website_order = request.website.sale_get_order()
                    if website_order:
                        website_order.sudo().unlink()
            else:
                return []
        return [latitude, longitude]
