import json
import logging
import requests
from markupsafe import Markup
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('aramex_ts', "Aramex")], ondelete={'aramex_ts': 'cascade'})
    am_service_group = fields.Selection([
        ('DOM', 'Domestic'),
        ('EXP', 'Express')], default="DOM", string="Service Group")
    am_dom_service_type = fields.Selection([
        ('SMP', 'Same day shipment'),
        ('EMD', 'Early morning delivery'),
        ('ONP', 'Overnight delivery'),
        ('PEC', 'Economy'),
        ('PEX', 'Road Express'),
    ], string="Domestic Service", help="Aramex Domestic Service")
    am_intl_service_type = fields.Selection([
        ('PPX', 'Priority Parcel Express'),
        ('PDX', 'Priority Document Express')], string="International Service", help="Aramex Product")
    am_payment_type = fields.Selection([
        ('P', 'Prepaid - payable by shipper'),
        ('3', 'Third Party')], default="P", string="Payment Method")
    am_waybill_template = fields.Selection([
        ('9201', 'Labels'),
        ('9202', 'A4 waybills')
    ], default='9201', string="Waybill Template")
    am_product_packaging_id = fields.Many2one("stock.package.type", string="Default Package Type")
    am_require_insurance = fields.Boolean(string="Insurance")

    def aramex_ts_prepare_request_data(self, shipper, recipient):
        self.ensure_one()
        request_data = {
            'email_address': self.shipping_partner_id.am_user_name,
            'password': self.shipping_partner_id.am_password,
            'account_number': self.shipping_partner_id.am_account_number,

            'sender_country_code': shipper.country_id.code,
            'sender_country_name': shipper.country_id.name,
            'sender_suburb': shipper.city,
            'sender_postal_code': shipper.zip,

            'receiver_country_code': recipient.country_id.code,
            'receiver_country_name': recipient.country_id.name,
            'receiver_suburb': recipient.city,
            'receiver_postal_code': recipient.zip,

            'payment_type': self.am_payment_type,
            'service_type': self.am_dom_service_type if self.am_service_group == 'DOM' else self.am_intl_service_type,
            'is_documents': False,
            'require_insurance': self.am_require_insurance,
        }
        return request_data

    def aramex_ts_prepare_shipment_request_data(self, shipper, recipient, total_value):
        self.ensure_one()
        request_data = {
            'sender_street_address': shipper.street or shipper.street2,
            'sender_other_address': shipper.street and shipper.street2 or '',
            'sender_state': shipper.state_id.name or shipper.city,
            'sender_name': shipper.name,
            'sender_contact_number': shipper.mobile or shipper.phone,
            'sender_contact_person': self.env.user.name,

            'receiver_street_address': recipient.street or recipient.street2,
            'receiver_other_address': recipient.street and recipient.street2 or '',
            'receiver_state': recipient.state_id.name or recipient.city,
            'receiver_name': recipient.parent_id.name if recipient.parent_id else recipient.name,
            'receiver_contact_person': recipient.name,
            'receiver_contact_number': recipient.mobile or recipient.phone,
            'receiver_email_address': recipient.email or '',

            'waybill_print_template': int(self.am_waybill_template),
            'waybill_pdf_fetch_type': 'URL',
            'is_import': False,
        }
        if self.am_require_insurance:
            request_data.update({'insurance_value': total_value})
        return request_data

    @api.model
    def aramex_ts_add_parcel(self, weight, package=False):
        parcel_dict = {'weight': weight, 'quantity': 1}
        # packaging_id = package.packaging_id if package and package.packaging_id else self.am_product_packaging_id
        # if packaging_id:
        #     parcel_dict.update({'length': packaging_id.length, 'width': packaging_id.width, 'height': packaging_id.height})
        return parcel_dict

    def aramex_ts_calculate_parcel_value(self, picking=False, order=False, package=False):
        customs_items = []
        parcel_value = 0.0
        aramex_currency = self.env['res.currency'].search([('name', '=', 'ZAR')], limit=1)
        if order:
            for line in order.order_line:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                parcel_value += line.price_subtotal
            return order.currency_id._convert(parcel_value, aramex_currency)
        elif picking and not package:
            for line in picking.move_line_ids:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                parcel_value += line.move_id.sale_line_id.price_subtotal
            return picking.sale_id.currency_id._convert(parcel_value, aramex_currency)
        elif picking and package:
            for line in picking.move_line_ids.filtered(lambda x: x.result_package_id == package):
                if line.product_id.type not in ['product', 'consu']:
                    continue
                parcel_value += line.move_id.sale_line_id.price_unit * line.quantity
            return picking.sale_id.currency_id._convert(parcel_value, aramex_currency)
        return customs_items

    def aramex_ts_send_rate_request(self, order, total_weight, max_weight):
        try:
            request_data = self.aramex_ts_prepare_request_data(order.warehouse_id.partner_id, order.partner_shipping_id)
            package_list = []
            parcel_value = self.aramex_ts_calculate_parcel_value(order=order)
            # if max_weight and total_weight > max_weight:
            #     total_package = int(total_weight / max_weight)
            #     last_package_weight = total_weight % max_weight
            #     total_package_count = total_package if not last_package_weight else (total_package + 1)
            #     for index in range(total_package):
            #         parcel_dict = self.aramex_ts_add_parcel(max_weight)
            #         if self.am_require_insurance:
            #             parcel_dict.update({'parcel_value': float_round(parcel_value / total_package_count, precision_digits=2)})
            #         package_list.append(parcel_dict)
            #     if last_package_weight:
            #         parcel_dict = self.aramex_ts_add_parcel(last_package_weight)
            #         if self.am_require_insurance:
            #             parcel_dict.update({'parcel_value': float_round(parcel_value / total_package_count, precision_digits=2)})
            #         package_list.append(parcel_dict)
            # else:
            parcel_dict = self.aramex_ts_add_parcel(total_weight)
            if self.am_require_insurance:
                parcel_dict.update({'parcel_value': float_round(parcel_value, precision_digits=2)})
            package_list.append(parcel_dict)
            request_data.update({'parcels': package_list})
            response = self.shipping_partner_id._aramex_send_request('GetRate', request_data, self.prod_environment, method="POST")
        except Exception as e:
            return {'success': False, 'price': 0.0, 'error_message': e, 'warning_message': False}
        if response.get('status_code') != 0:
            error_message = "Message: {} ({})".format(response.get('status_description'), response.get('status_code'))
            return {'success': False, 'price': 0.0, 'error_message': error_message, 'warning_message': False}
        shipping_charge = response.get('rate')
        if not shipping_charge:
            return {'success': False, 'price': 0.0, 'error_message': "Rate isn't available for selected service.", 'warning_message': False}
        rate_currency = self.env['res.currency'].search([('name', '=', 'ZAR')], limit=1)
        if order.currency_id != rate_currency:
            shipping_charge = rate_currency._convert(shipping_charge, order.currency_id)
        return {'success': True,
                'price': float(shipping_charge),
                'error_message': False,
                'warning_message': False}

    def _aramex_ts_convert_weight(self, weight):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if weight_uom_id != self.env.ref('uom.product_uom_kgm'):
            weight = weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_kgm'), round=False)
        return float_round(weight, precision_digits=2)

    def aramex_ts_rate_shipment(self, order):
        check_value = self.check_required_value_shipping_request(order)
        if check_value:
            return {'success': False, 'price': 0.0, 'error_message': check_value, 'warning_message': False}
        est_weight_value = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0
        total_weight = self._aramex_ts_convert_weight(est_weight_value)
        max_weight = 0.0  # self._aramex_ts_convert_weight(self.am_product_packaging_id.max_weight)
        return self.aramex_ts_send_rate_request(order, total_weight, max_weight)

    def aramex_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            attachments = []
            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            total_bulk_weight = self._aramex_ts_convert_weight(picking.weight_bulk)
            total_parcel_value = self.aramex_ts_calculate_parcel_value(picking=picking)
            try:
                # picking.check_packages_are_identical()
                request_data = self.aramex_ts_prepare_request_data(picking.picking_type_id.warehouse_id.partner_id, picking.partner_id)
                package_list = []
                if picking.package_ids:
                    # Create all packages
                    for package in picking.package_ids:
                        package_weight = self._aramex_ts_convert_weight(package.shipping_weight)
                        parcel_dict = self.aramex_ts_add_parcel(package_weight)
                        if self.am_require_insurance:
                            parcel_dict.update({'parcel_value': self.aramex_ts_calculate_parcel_value(picking=picking, package=package)})
                        package_list.append(parcel_dict)
                # Create one package with the rest (the content that is not in a package)
                if total_bulk_weight:
                    parcel_dict = self.aramex_ts_add_parcel(total_bulk_weight)
                    if self.am_require_insurance:
                        parcel_dict.update({'parcel_value': self.aramex_ts_calculate_parcel_value(picking=picking)})
                    package_list.append(parcel_dict)
                request_data.update({'parcels': package_list})
                response = self.shipping_partner_id._aramex_send_request('GetRate', request_data, self.prod_environment, method="POST")
                if response.get('status_code') != 0:
                    error_message = "Message: {} ({})".format(response.get('status_description'), response.get('status_code'))
                    raise UserError(_(error_message))
                exact_price = response.get('rate')
                request_data.update(self.aramex_ts_prepare_shipment_request_data(picking.picking_type_id.warehouse_id.partner_id, picking.partner_id, total_parcel_value))
                request_data.update(
                    {'sender_reference1': picking.name, 'sender_reference2': picking.sale_id.name or '', 'receiver_reference1': picking.sale_id.name or picking.name})
                shipment_response = self.shipping_partner_id._aramex_send_request('SubmitWaybill', request_data, self.prod_environment, method="POST")
                if shipment_response.get('status_code') != 0:
                    error_message = "Message: {} ({})".format(response.get('status_description'), response.get('status_code'))
                    raise UserError(_(error_message))
                tracking_number = shipment_response.get('waybill_number')
                label_url = shipment_response.get('label_print')
                label_binary_data = requests.get(label_url).content
                attachments.append(('Aramex-%s.%s' % (tracking_number, 'pdf'), label_binary_data))
                rate_currency = self.env['res.currency'].search([('name', '=', 'ZAR')], limit=1)
                if rate_currency and order.currency_id != rate_currency:
                    exact_price = rate_currency._convert(exact_price, order.currency_id, company)
                msg = (_('<b>Shipment created!</b><br/><b>Tracking Number:</b> %s') % tracking_number)
                picking.message_post(body=Markup(msg), attachments=attachments)
            except Exception as e:
                raise UserError(e)
            res = res + [{'exact_price': exact_price, 'tracking_number': tracking_number}]
        return res

    def aramex_ts_get_tracking_link(self, picking):
        tracking_numbers = picking.carrier_tracking_ref.split(',')
        if len(tracking_numbers) == 1:
            return 'https://www.aramex.com/za/en/track/results?mode=0&ShipmentNumber=%s' % picking.carrier_tracking_ref
        tracking_urls = []
        for tracking_number in tracking_numbers:
            tracking_urls.append((tracking_number, 'https://www.aramex.com/za/en/track/results?mode=0&ShipmentNumber=%s' % tracking_number))
        return json.dumps(tracking_urls)

    def aramex_ts_cancel_shipment(self, picking):
        raise UserError(_("Sorry! You can't cancel Aramex shipment anymore. Please contact Aramex support!"))
