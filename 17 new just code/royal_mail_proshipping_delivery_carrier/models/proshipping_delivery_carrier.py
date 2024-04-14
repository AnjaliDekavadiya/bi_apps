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

# The Shipping AccountType can use sandbox or production
TOKEN_URL = "https://authentication.proshipping.net/connect/token" # Authentication
SHIPMENT_URL = "https://api.proshipping.net/v4/shipments/rm" # Create shipment


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"


    def royal_mail_pro_rate_shipment(self, order):
        price = self.royal_pro_fixed_price
        return {
            'success': True,
            'price': price,
            'error_message': False,
            'warning_message': False
        }
    
    def request_royal_mail_pro_token(self):
        config = self.wk_get_carrier_settings([
            'royal_pro_grant_type',
            'royal_pro_client_id',
            'royal_pro_client_secret',])
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'grant_type' : config["royal_pro_grant_type"],
            'client_id' : config["royal_pro_client_id"],
            'client_secret' : config["royal_pro_client_secret"]
        }
        response = requests.post(TOKEN_URL, data=payload, headers=headers) # API call
        return response
    
    def get_royal_mail_pro_token(self):
        request_token = self.request_royal_mail_pro_token()
        data = json.loads(request_token.text)
        if request_token.status_code == 200:
            return data['access_token']
        else:
            raise UserError(f'Token not valid. Invalid Credentials. {data["error"]}')
        
    def calculate_package_declared_value(self, pickings, package):
        total_price = 0.0
        for each in package.quant_ids:
            sale_price = 0.0
            for order_line in pickings.sale_id.order_line:
                if order_line.product_id.id ==  each.product_id.id:
                    sale_price = order_line.price_unit
                    total_price += sale_price * each.quantity
        return total_price
    
    def royal_mail_pro_construct_package_data(self, pickings):
        packages = []
        items = []
        PackageOccurrence = 1
        for each in pickings.package_ids:
            if self.royal_pro_service_type_id.is_international:
                pack_items = self.royal_mail_pro_construct_items_data(PackageOccurrence, each, pickings)
                items.extend(pack_items)
            package = {
                'PackageOccurrence' : PackageOccurrence,
                'PackageType' : each.package_type_id.shipper_package_code,
                'DeclaredValue' : self.calculate_package_declared_value(pickings, each),  # If provided, the value must be equal or less than the sum of all item values.
                'DeclaredWeight' : round(each.shipping_weight, 2),
            }
            packages.append(package)
            PackageOccurrence += 1
        return {'packages': packages, 'items': items}

    
    def royal_mail_pro_construct_items_data(self, Occurrence, package, pickings):
        Items = []
        for each in package.quant_ids:
            sale_price = 0.0
            for order_line in pickings.sale_id.order_line:
                if order_line.product_id.id ==  each.product_id.id:
                    sale_price = order_line.price_unit
            if not each.product_id.hs_code:
                raise ValidationError(f'Missing HS code for {each.product_id.name}')
            if not each.product_id.country_of_origin.code:
                raise ValidationError(f'Missing Country Origin for {each.product_id.name}')
            item = dict(
                SkuCode = each.product_id.default_code,
                PackageOccurrence = Occurrence,
                Quantity = int(each.quantity),
                Description = each.product_id.name[0:254],
                Value = sale_price, # Individual value of the item.
                Weight = each.product_id.weight, # Individual item weight.
                HSCode = each.product_id.hs_code,
                CountryOfOrigin = each.product_id.country_of_origin.code,
            )
            Items.append(item)
        return Items
        

    def royal_mail_pro_construct_shipment_data(self, pickings):
        packages_data = self.royal_mail_pro_construct_package_data(pickings)

        receiver = pickings.partner_id
        self.wk_validate_object_fields(receiver, ['name', 'email', 'phone', 'city', 'zip', 'country_id'])
        receiver_address = self.get_shipment_recipient_address(picking=pickings)
        shipper = pickings.picking_type_id.warehouse_id.partner_id
        self.wk_validate_object_fields(shipper, ['phone','city', 'zip', 'country_id'])
        shipper_address = self.get_shipment_shipper_address(picking=pickings)


        Shipper = dict(
            ShippingAccountId = self.royal_pro_ShippingAccountId,
            Reference1 = f'{pickings.origin} {pickings.name}',
        )
        if not self.is_royal_pro_use_account_address:
            Address = dict(
                ContactName = shipper_address['name'],
                CompanyName = shipper_address['name'],
                ContactEmail = shipper_address['email'],
                ContactPhone = shipper_address['phone'],
                Line1 = shipper_address['street'],
                Town = shipper_address['city'],
                Postcode = shipper_address['zip'],
                CountryCode = shipper_address['country_code']
            )
            Shipper.update({'Address':Address})

        if self.royal_pro_ShippingLocationId:
            Shipper.update({'ShippingLocationId':self.royal_pro_ShippingLocationId})
        if shipper.vat:
            Shipper.update({'VatNumber' : shipper.vat})
        if self.royal_pro_eori_number:
            Shipper.update({'EoriNumber' : self.royal_pro_eori_number})
        
        currency_id = self.get_shipment_currency_id(pickings=pickings)
        uom = self.uom_id.name
        if uom not in ['cm', 'mm']:
            raise ValidationError("Please change the Odoo Product UoM from shipping method. only 'mm' and 'cm' are allowed.")
        ShipmentInformation = dict(
            LabelFormat = self.royal_pro_labelformat,
            ContentType = self.royal_pro_service_type_id.content_type,
            ServiceCode = self.royal_pro_service_type_id.product_id.code,
            DescriptionOfGoods = self.royal_pro_DescriptionOfGoods, #TODO
            ShipmentDate = pickings.scheduled_date.strftime("%Y-%m-%d"), # "2023-10-12"
            CurrencyCode = currency_id.name,
            WeightUnitOfMeasure = self.delivery_uom, # KG
            DimensionsUnitOfMeasure = uom.upper(), # MM | CM
        )
        Destination = {
            'Address': dict(
                ContactName=receiver_address.get("name"),
                ContactEmail=receiver_address.get("email"),
                ContactPhone=receiver_address.get("phone"),
                Line1=receiver_address.get("street"),
                Town=receiver_address.get("city"),
                Postcode=receiver_address.get("zip"),
                CountryCode=receiver_address.get("country_code"),
            )
        }
        if receiver.vat:
            Destination.update({'VatNumber':receiver.vat})
        payload = {
            "ShipmentInformation" : ShipmentInformation,
            "Shipper" : Shipper,
            "Destination" : Destination,
            "Packages" : packages_data.get('packages'),
        }
        if self.royal_pro_service_type_id.is_international:
            customs = dict(
                ReasonForExport = self.royal_pro_service_type_id.reason_for_export,
                Incoterms = self.royal_pro_service_type_id.incoterms,
            )
            payload.update({'Items':packages_data.get('items'), 'Customs': customs})

        return payload

    def royal_mail_pro_construct_api_header(self, token):
        headers = {
            "content-type": "application/json",
	        "Authorization": f'bearer {token}',
        }
        return headers
    
    def request_royal_mail_pro_create_shipment(self, headers, payload):
        response = requests.post(SHIPMENT_URL, data=json.dumps(payload), headers=headers) # API call
        if response.status_code == 200:
            return json.loads(response.content)
        elif response.status_code == 400:
            raise UserError(response.content)
        else:
            raise UserError(f'Something with the data sent in API request. ==> {response.content}')

    def royal_mail_pro_create_shipment(self, pickings):
        shipment_payload = self.royal_mail_pro_construct_shipment_data(pickings)
        token = self.get_royal_mail_pro_token()
        headers = self.royal_mail_pro_construct_api_header(token)
        shipment_response = self.request_royal_mail_pro_create_shipment(headers, shipment_payload)
        return shipment_response
        

    def royal_mail_pro_send_shipping(self, pickings):
        result = {
            'exact_price': 0,
            'weight': 0,
            'date_delivery': None,
            'tracking_number': '',
            'attachments': []
        }
        response = self.royal_mail_pro_create_shipment(pickings)
        TrackingNumber = f''
        TrackingUrl = f''
        for pack in response.get('Packages'):
            TrackingNumber = f'{TrackingNumber}, {pack["TrackingNumber"]}'
            TrackingUrl = f'{TrackingUrl}, {pack["CarrierTrackingUrl"]}'
        result['exact_price'] =  0
        result['weight'] = 0.0
        result['tracking_number'] = TrackingNumber[1:]
        label_format = ''
        if self.royal_pro_labelformat.find('pdf') > 0:
            label_format = '.pdf'
        elif self.royal_pro_labelformat.find('zpl') > 0:
            label_format = '.zpl'
        elif self.royal_pro_labelformat.find('png') > 0:
            label_format = '.png'
        result['attachments'] = [('Royalmail-' + pickings.origin + label_format, (base64.b64decode(response.get('Labels'))))]
        if response.get('Documents'):
            result['attachments'].append(('Royalmail-doc-' + pickings.origin + label_format, (base64.b64decode(response.get('Documents')))))
        pickings.message_post(
            body = TrackingUrl[1:],
            subject = "Tracking URL",
        )
        return result
    
    def royal_mail_pro_get_tracking_link(self, pickings):
        if pickings.carrier_tracking_ref.find(',') == -1:
            return f"https://www.royalmail.com/track-your-item#/tracking-results/{pickings.carrier_tracking_ref}"
        else:
            return f"https://www.royalmail.com/track-your-item"
    
    def royal_mail_pro_cancel_shipment(self,pickings):
        raise ValidationError('This feature is not supported by Royal Mail Pro Shipping.')
