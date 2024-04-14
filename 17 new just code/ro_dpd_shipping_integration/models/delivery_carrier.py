import requests
import json
from odoo.exceptions import ValidationError, UserError
from odoo import fields, models, api, _
import logging

_logger = logging.getLogger("RO DPD")


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('dpd_ro', 'DPD RO')], ondelete={'dpd_ro': 'set default'})
    dpd_service = fields.Many2one('dpd.services', string="DPD Services")
    courier_service_payer = fields.Selection([('SENDER', 'SENDER'),
                                              ('RECIPIENT', 'RECIPIENT'),
                                              ('THIRD_PARTY', 'THIRD PARTY')])
    label_paper_size = fields.Selection([('A4', 'A4'),
                                         ('A6', 'A6'),
                                         ('A4_4xA6', 'A4_4xA6'), ])

    def dpd_ro_rate_shipment(self, order):
        """This Method Is Used For Get Live Rate"""
        return {'success': True, 'price': 0.0, 'error_message': False, 'warning_message': False}

    def dpd_ro_body_request_data(self, picking):
        """ This Method Used For Collect Request Data Of Label Request
        """
        sender_address = picking.picking_type_id.warehouse_id.partner_id
        receiver_address = picking.partner_id

        body = {
            "userName": self.company_id.username,
            "password": self.company_id.password,
            "service": {
                "serviceId": self.dpd_service.service_id,
            },
            "content": {
                "parcelsCount": picking.no_of_labels,
                "totalWeight": picking.shipping_weight or 0,
                "contents": "Furniture",
                "package": "BOX"
            },
            "payment": {
                "courierServicePayer": self.courier_service_payer
            },
            "recipient": {
                "phone1": {
                    "number": receiver_address.phone or ""
                },
                "privatePerson": True,
                "clientName": receiver_address.name or "",
                "contactName": receiver_address.name or "",
                "email": receiver_address.email or "",
                "address": {
                    "siteName": receiver_address.city or "",
                    "streetType": "str.",
                    "streetName": receiver_address.street,
                    "streetNo": receiver_address.street2
                }
            },
            "ref1": picking.origin,
        }
        json_data = json.dumps(body)
        return json_data

    def print_label_service(self, parcel_list):
        parcels = []
        for parcel in parcel_list:
            parcels.append({
                "parcel": {
                    "id": parcel
                }

            })
        payload = {
            "userName": self.company_id.username,
            "password": self.company_id.password,
            "paperSize": self.label_paper_size,
            "parcels": parcels
        }
        json_data = json.dumps(payload)
        return json_data

    def dpd_ro_send_shipping(self, pickings):
        response = []
        try:
            request_data = self.dpd_ro_body_request_data(pickings)
            _logger.info(request_data)
            api_url = "%s/shipment" % (self.company_id.dpd_api_url)
            headers = {
                'Content-Type': 'application/json;charset=utf-8'}
            response_data = requests.request(method="POST", url=api_url, headers=headers, data=request_data)
            _logger.info(response_data)
            if response_data.status_code in [200, 201]:
                response_body = response_data.json()
                _logger.info(response_body)
                if response_body.get('error'):
                    if response_body.get('error').get('code') > 0:
                        raise ValidationError(response_body.get('error').get('message'))
                parcel_list = []
                parcels = response_body.get('parcels')
                for parcel in parcels:

                    parcel_list.append((parcel.get('id')))
                pickings.carrier_tracking_ref = response_body.get('id')
                pickings.parcel_ids = ",".join(parcel_list)

                # from here print label code start
                print_lable_request = self.print_label_service(parcel_list)
                _logger.info(print_lable_request)
                label_api_url = "%s/print" % (self.company_id.dpd_api_url)
                response_data = requests.request(method="POST", url=label_api_url, headers=headers,
                                                 data=print_lable_request)
                _logger.info(response_data)
                pdf_data = response_data.content
                mesage_body = ("Pdf Sucessfully Generated ")
                pickings.message_post(body=mesage_body,
                                      attachments=[('%s.pdf' % (pickings.id), pdf_data)])
                shipping_data = {'exact_price': 0.0, 'tracking_number': pickings.carrier_tracking_ref}
                response = [shipping_data]
                return response
            else:
                raise ValidationError(response_data.text)
        except Exception as e:
            raise ValidationError(_("\n Response Data : %s") % (e))

    def dpd_ro_get_tracking_link(self, picking):
        """This Method Is Used For Track Parcel"""
        link = "https://tracking.dpd.ro/?shipmentNumber="
        res = '%s%s' % (link, picking.parcel_ids)
        return res

    def dpd_ro_cancel_shipment(self, picking):

        payload = {
            "userName": self.company_id.username,
            "password": self.company_id.password,
            "shipmentId": picking.carrier_tracking_ref,
            "comment": "Cancel Shipment"
        }
        api_url = "%s/shipment/cancel" % (self.company_id.dpd_api_url)
        headers = {
            'Content-Type': 'application/json;charset=utf-8'}
        response_data = requests.request(method="POST", url=api_url, headers=headers, data=json.dumps(payload))
        _logger.info(response_data)
        if response_data.status_code in[200,201]:
            response_body = response_data.json()
            _logger.info(response_body)
            if response_body.get('error'):
                raise ValidationError(response_body.get('error').get('message'))
            else:
                _logger.info("Order Cancel Successfully")
                return True




