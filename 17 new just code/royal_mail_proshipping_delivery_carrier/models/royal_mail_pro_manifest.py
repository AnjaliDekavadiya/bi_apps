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
import base64
import json
import requests
import logging
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
_logger = logging.getLogger(__name__)

# Manifests (POST) https://api.proshipping.net/v4/manifests/{carrier_code}
MANIFESTS_URL = "https://api.proshipping.net/v4/manifests/RM"

class Proshippingmanifest(models.Model):
    _name = "delivery.royal_mail_pro.manifest"
    _description = "Delivery Carrier Royal mail Pro Manifest"
    _inherit = 'mail.thread'

    name = fields.Char(string="Manifest Number", required=True)
    AccountNumber = fields.Char(string="Account Number")
    CarrierCode = fields.Char(string="Carrier Code")
    Service = fields.Char(string="Service")
    TotalWeight = fields.Float(string="Total Weight")
    TotalShipments = fields.Integer(string="Total Shipments")
    TotalItems = fields.Integer(string="Total Items")
    ManifestDate = fields.Char(string="Manifest Date")

    def create_manifest(self, headers, ShippingAccountId):
        payload = {
            "ShippingAccountId": ShippingAccountId
        }
        response = requests.post(MANIFESTS_URL, data=json.dumps(payload), headers=headers) # API call
        if response.status_code == 200:
            _logger.info(f'manifest_response------------{response.content}')
            return json.loads(response.content)
        elif response.status_code == 400:
            _logger.info(f'manifest error-----------{response.content}')
            raise UserError(response.content)
        else:
            raise UserError(f'Failed to create manifest. ==> {response.content}')
        
    def save_manifest(self, res_data):
        data = res_data[0]
        vals = {
            'name': data.get('ManifestNumber'),
            'AccountNumber': data['ShippingAccount']['AccountNumber'],
            'CarrierCode': data.get('CarrierCode'),
            'Service': data.get('Service'),
            'TotalWeight': data.get('TotalWeight', 0.0),
            'TotalShipments': data.get('TotalShipments', 0),
            'TotalItems': data.get('TotalItems', 0),
            'ManifestDate': data.get('ManifestDate'),
        }
        new_rec = self.create(vals)
        return new_rec

    def cron_create_manifest(self):
        delivery_ids = self.env['delivery.carrier'].search([('delivery_type', '=', 'royal_mail_pro')])
        ShippingAccountId = []
        for rec in delivery_ids:
            if rec.royal_pro_ShippingAccountId not in ShippingAccountId:
                ShippingAccountId.append(rec.royal_pro_ShippingAccountId)
                token = rec.get_royal_mail_pro_token()
                headers = rec.royal_mail_pro_construct_api_header(token)
                manifest_res = self.create_manifest(headers, rec.royal_pro_ShippingAccountId)
                create_manifest_rec = self.save_manifest(manifest_res)
                my_attachment = self.env['ir.attachment'].create({
                    'datas': manifest_res[0]["ManifestImage"],
                    'name': f'RMP-{manifest_res[0]["ManifestNumber"]}.pdf',
                    'res_model': 'delivery.royal_mail_pro.manifest',
                    'res_id': create_manifest_rec.id,
                })
                create_manifest_rec.message_post(
                    body='Manifest for Royal Mail Pro',
                    subject='Attachments of Manifest',
                    attachment_ids=[my_attachment.id]
                )
