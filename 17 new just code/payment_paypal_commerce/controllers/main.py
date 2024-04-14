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

from odoo import http, _
from odoo.http import route, request, Response
from odoo.exceptions import UserError, UserError
from datetime import datetime, timedelta
from odoo.tools import float_round
import werkzeug
import requests
import json
import jwt
import logging
_logger = logging.getLogger(__name__)

BRANDED_COUNTRIES = ['AT','CA','DE','IE']
PARTNER_ATTRIBUTION_ID = "Webkul_SP_SB"

class PaypalCommerceController(http.Controller):

    def check_partner_basic_details(self, partner):
        empty_fields_list = []
        if not partner.email:
            empty_fields_list.append("Email")
        if not partner.country_id or not partner.state_id or not partner.zip:
            empty_fields_list.append("Address")
        return empty_fields_list

    def get_seller_amt_values(order):
        total_seller_amt = 0.0
        shipping_amt = 0.0
        return_dict = {
            "sellers_data": {},
            "admin_amt": 0.0
        }
        for line in order.order_line:
            seller = line.product_id.marketplace_seller_id
            if line.is_delivery:
                shipping_amt += line.price_total
            if seller and seller.commerce_merchant_id and seller.commerce_authorized:
                seller_amt = request.env["account.move"].sudo().calculate_commission(line.price_subtotal, seller.id)
                admin_amt = line.price_total - seller_amt
                if return_dict["sellers_data"].get(seller.id):
                    return_dict["sellers_data"].get(seller.id)["amt"] += line.price_total
                    return_dict["sellers_data"].get(seller.id)["admin_amt"] += admin_amt
                else:
                    return_dict["sellers_data"].update({seller.id: {
                        "merchant_id": seller.commerce_merchant_id,
                        "admin_amt": admin_amt,
                        "email": seller.email,
                        "amt": line.price_total
                    }})
        if shipping_amt:
            seller_data = return_dict['sellers_data']
            shipping_per_seller_amt = shipping_amt/len(seller_data)
            for seller_id in seller_data.keys():
                return_dict["sellers_data"].get(seller_id)["admin_amt"] += shipping_per_seller_amt
                return_dict["sellers_data"].get(seller_id)["amt"] += shipping_per_seller_amt
        return return_dict

    def registered_mppaypal_commerce_webhook(provider_id):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        access_token = provider_id.sudo().paypal_commerce_get_access_token()
        paypal_base_url = provider_id.get_paypal_commerce_url()
        header = {
            "Content-Type" : "application/json",
            "Authorization" : "Bearer " + access_token,
            "PayPal-Partner-Attribution-Id": PARTNER_ATTRIBUTION_ID
        }
        data = {
            "url": base_url+"/mppaypal/commerce/webhook/interface",
            "event_types": [
                {"name": "MERCHANT.ONBOARDING.COMPLETED"},
                {"name": "MERCHANT.PARTNER-CONSENT.REVOKED"},
                {"name": "CHECKOUT.ORDER.COMPLETED"},
                {"name": "PAYMENT.CAPTURE.COMPLETED"},
                {"name": "PAYMENT.CAPTURE.DENIED"},
                {"name": "PAYMENT.CAPTURE.REFUNDED"},
                {"name": "PAYMENT.REFERENCED-PAYOUT-ITEM.COMPLETED"},
                {"name": "PAYMENT.REFERENCED-PAYOUT-ITEM.FAILED"}
            ]
        }
        data = json.dumps(data)
        url = paypal_base_url+"/v1/notifications/webhooks"
        response = requests.post(url, data=data, headers=header)
        res_data = response.json()
        if res_data:
            webhook_id = res_data.get("id")
            if webhook_id:
                provider_id.write({"paypal_commerce_webhook_id": webhook_id})
            else:
                # Raise Error
                pass
        return

    def paypal_commerce_create_order(provider_id, data):
        access_token = provider_id.sudo().paypal_commerce_get_access_token()
        paypal_base_url = provider_id.get_paypal_commerce_url()
        disbursement_mode = "INSTANT"
        if provider_id.paypal_commerce_delay_payment:
            disbursement_mode = "DELAYED"
        if access_token:
            purchase_units = []
            if data.get('order'):
                amount_dict = PaypalCommerceController.get_seller_amt_values(data['order'])
                reference = data['reference']+'/' if data.get('reference') else ''
                if amount_dict.get("sellers_data") and amount_dict.get("sellers_data").values():
                    for seller_id, wk_mp_dict in amount_dict.get("sellers_data").items():
                        purchase_units.append({
                            "reference_id" : reference + str(seller_id),
                            "amount" : {
                                "value" : float_round(wk_mp_dict.get("amt", 0.0), precision_digits=2),
                                "currency_code": data['currency_code']
                            },
                            "payee" : {
                                "email" : wk_mp_dict.get("email"),
                                "merchant_id" : wk_mp_dict.get("merchant_id")
                            },
                            "payment_instruction" : {
                                "platform_fees" : [{
                                   "amount":{
                                      "currency_code": data['currency_code'],
                                      "value": float_round(wk_mp_dict.get("admin_amt", 0.0), precision_digits=2)
                                   }
                                }],
                                "disbursement_mode" : disbursement_mode
                            }
                        })
            data = {
                "intent" : "CAPTURE",
                "purchase_units" : purchase_units
            }
            header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + access_token,
                "PayPal-Partner-Attribution-Id": PARTNER_ATTRIBUTION_ID
            }
            url = paypal_base_url + "/v2/checkout/orders"
            response = requests.post(url, json=data, headers=header)
            res_data = response.json()
            if res_data:
                return res_data.get("id")
        return None

    def paypal_commerce_refund_order(provider_id, order_id, merchant_id):
        provider_id = provider_id.sudo()
        access_token = provider_id.paypal_commerce_get_access_token()
        paypal_base_url = provider_id.get_paypal_commerce_url()
        auth_assersion_data = {
            'iss': provider_id.paypal_commerce_client_id,
            'payer_id': merchant_id
        }
        auth_assersion_token = jwt.encode(auth_assersion_data, '', algorithm='HS256')
        if access_token:
            header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + access_token,
                "PayPal-Auth-Assertion": auth_assersion_token,
                "PayPal-Partner-Attribution-Id": PARTNER_ATTRIBUTION_ID
            }
            url = paypal_base_url + "/v2/payments/captures/" + order_id + "/refund"
            response = requests.post(url, json={}, headers=header)
            res_data = response.json()
            if res_data:
                if res_data.get('debug_id'):
                    return {
                        'error_msg': "Sorry, but something went wrong. Paypal debug ID: %s" % res_data["debug_id"]
                    }
                else:
                    return {
                        'is_refunded': True,
                        'refund_status': res_data.get('status'),
                        'refund_id': res_data.get('id')
                    }
        return False

    def paypal_commerce_release_seller_payment(provider_id, transaction_id):
        provider_id = provider_id.sudo()
        access_token = provider_id.paypal_commerce_get_access_token()
        paypal_base_url = provider_id.get_paypal_commerce_url()
        data = {
            "reference_id": transaction_id,
            "reference_type": "TRANSACTION_ID"
        }
        if access_token:
            header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + access_token,
                "PayPal-Partner-Attribution-Id": PARTNER_ATTRIBUTION_ID
            }
            url = paypal_base_url + "/v1/payments/referenced-payouts-items"
            response = requests.post(url, json=data, headers=header)
            res_data = response.json()
            if res_data:
                if res_data.get('debug_id'):
                    return {
                        'error_msg': "Sorry, but something went wrong. Paypal debug ID: %s" % res_data["debug_id"]
                    }
                else:
                    if res_data.get('processing_state') and res_data['processing_state'].get('status'):
                        status = res_data['processing_state']['status']
                        if status == 'SUCCESS':
                            return {
                                'is_released': True,
                                'released_status': status,
                            }
                        else:
                            return {
                                'released_status': status,
                            }
                    else:
                        return {
                            'error_msg': "Sorry, but something went wrong."
                        }
        return False

    def paypal_commerce_update_access_token(provider_id):
        data = {
            "grant_type" : "client_credentials"
        }
        auth = (provider_id.paypal_commerce_client_id, provider_id.paypal_commerce_secret_id)
        paypal_base_url = provider_id.get_paypal_commerce_url()
        url = paypal_base_url+"/v1/oauth2/token"
        response = requests.post(url, params=data, auth=auth)
        res_data = response.json()
        if res_data:
            provider_id.paypal_commerce_access_token = res_data.get('access_token')
            expires_in = res_data.get('expires_in')
            if expires_in:
                provider_id.paypal_commerce_expiry_date = datetime.now() + timedelta(seconds=expires_in)
        return

    def update_paypal_commerce_tx_data(self, res_data):
        data = {}
        update_receivers = []
        for p_unit in res_data.get('purchase_units'):
            if p_unit.get('payments') and p_unit['payments'].get('captures'):
                captures = p_unit['payments']['captures'][0]
                update_receivers.append({
                    'paypal_id' : captures.get('id'),
                    'status' : captures.get('status')
                })
        data.update({
            'provider_reference' : res_data.get('id'),
            'state' : res_data.get('status'),
            'update_receivers' : update_receivers
        })
        request.env['payment.transaction'].sudo().form_feedback(data, 'paypal_commerce')

    def update_paypal_commerce_onboard_data(self, marchant_id, seller=None):
        if not seller:
            seller = request.env["res.partner"].sudo().search([('commerce_merchant_id','=',marchant_id)],limit=1)
        if seller:
            payment_provider = request.env["payment.provider"].sudo().search([("code", "=", "paypal_commerce")], limit=1)
            config_marchant_id = payment_provider.paypal_merchant_id
            access_token = payment_provider.sudo().paypal_commerce_get_access_token()
            paypal_base_url = payment_provider.get_paypal_commerce_url()
            header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + access_token,
                "PayPal-Partner-Attribution-Id": PARTNER_ATTRIBUTION_ID
            }
            url = paypal_base_url+"/v1/customer/partners/"+config_marchant_id+"/merchant-integrations/"+marchant_id
            response = requests.get(url, headers=header)
            res_data = response.json()
            if res_data:
                payments_receivable = res_data.get('payments_receivable')
                primary_email_confirmed = res_data.get('primary_email_confirmed')
                oauth_integrations = res_data.get('oauth_integrations')
                vals = {}
                if primary_email_confirmed:
                    vals['primary_email_confirmed'] = True
                    if payments_receivable and oauth_integrations:
                        vals['commerce_authorized'] = True
                else:
                    vals.update({
                        'primary_email_confirmed': False,
                        'commerce_authorized' : False
                    })
                seller.write(vals)

    def remove_seller_authorization(merchant_id):
        seller = request.env["res.partner"].sudo().search([('commerce_merchant_id','=',merchant_id)],limit=1)
        seller.write({
            'primary_email_confirmed': False,
            'commerce_authorized': False
        })

    @http.route(['/paypal/commerce/sdk/url',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_commerce_sdk_url(self, **post):
        pricelist = request.session.get('website_sale_current_pl')
        provider_obj = request.env['payment.provider'].search([('code','=','paypal_commerce')], limit=1)
        # paypal_base_url = provider_obj.get_paypal_commerce_url()
        order = request.website.sale_get_order()
        marchant_ids = order.get_paypal_commerce_marchant_ids()
        if provider_obj and marchant_ids and provider_obj.paypal_commerce_client_id:
            url = "https://www.paypal.com/sdk/js?client-id=" + str(provider_obj.paypal_commerce_client_id)
            if len(marchant_ids) == 1:
                url = url + "&merchant-id=" + marchant_ids[0]
                return {'url': url, 'marchant_ids': False}
            else:
                url = url + "&merchant-id=*"
                return {'url': url, 'marchant_ids': ",".join(marchant_ids)}
        # if not marchant_ids:
        # return {'Error':"No marchant product is added!"}
        return False

    @http.route('/paypal_commerce/oauth/callback', type='http', auth="public", website=True)
    def paypal_commerce_aouth_return(self, **post):
        tracking_id = post.get('merchantId')
        merchant_id = post.get('merchantIdInPayPal')
        seller = request.env.user.partner_id
        seller.sudo().write({
            "commerce_tracking_id" : tracking_id,
            "commerce_merchant_id" : merchant_id,
        })
        self.update_paypal_commerce_onboard_data(merchant_id, seller)
        paypal_connect_menu_id = request.env['ir.model.data'].get_object_reference('payment_paypal_commerce', 'paypal_commerce_setup_menu')[1]
        redirect = "/web#menu_id=" + str(paypal_connect_menu_id)
        return http.redirect_with_hash(redirect)

    @http.route('/paypal_commerce/authorize/json', type='json', auth='public')
    def paypal_commerce_authorize_json(self, **post):
        payment_provider = request.env["payment.provider"].sudo().search([("code", "=", "paypal_commerce")], limit=1)
        seller = request.env.user.partner_id
        if seller.commerce_tracking_id and seller.commerce_merchant_id:
            return {
                "status": "connected",
                "auth_status": seller.commerce_authorized,
                "email_status": seller.primary_email_confirmed
            }
        empty_fields_list = self.check_partner_basic_details(partner=seller)
        if empty_fields_list:
            error_msg = "Some basic details are required to connect with paypal. Please update these details(%s) in your profile and then try again." % ",".join(empty_fields_list)
            return {"status": "error", "error_msg": error_msg}
        if payment_provider:
            access_token = payment_provider.with_context(new_access_token=True).sudo().paypal_commerce_get_access_token()
            paypal_base_url = payment_provider.get_paypal_commerce_url()
            if access_token:
                paypal_product = "PPCP"
                country_code = seller.country_id.code
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                if country_code in BRANDED_COUNTRIES:
                    paypal_product = "EXPRESS_CHECKOUT"
                data = {
                    "tracking_id": str(seller.id),
                    "email": seller.email,
                    "operations": [
                        {
                            "operation": "API_INTEGRATION",
                            "api_integration_preference": {
                                "rest_api_integration": {
                                    "integration_method": "PAYPAL",
                                    "integration_type": "THIRD_PARTY",
                                    "third_party_details": {
                                        "features": [
                                            "PAYMENT",
                                            "REFUND",
                                            "PARTNER_FEE",
                                            "DELAY_FUNDS_DISBURSEMENT",
                                            "READ_SELLER_DISPUTE",
                                            "UPDATE_SELLER_DISPUTE"
                                        ]
                                    }
                                }
                            }
                        }
                    ],
                    "products": [
                        paypal_product
                    ],
                    "legal_consents": [
                        {
                            "type": "SHARE_DATA_CONSENT",
                            "granted": True
                        }
                    ],
                    "partner_config_override": {
                      "return_url": base_url+"/paypal_commerce/oauth/callback",
                      "return_url_description": "The url to return the merchant after the paypal onboarding process."
                    },
                    "individual_owners" : [
                        {
                            "addresses": [
                                {
                                    "address_line_1": seller.street if seller.street else "",
                                    "address_line_2": seller.street2 if seller.street2 else "",
                                    "admin_area_2": seller.city if seller.city else "",
                                    "admin_area_1": seller.state_id.code if seller.state_id else "",
                                    "postal_code": seller.zip if seller.zip else "",
                                    "country_code": country_code if country_code else "",
                                    "type": "HOME"
                                }
                            ],
                            "type": "PRIMARY"
                        }
                    ]
                }
                header = {
                    "Content-Type" : "application/json",
                    "Authorization" : "Bearer " + access_token,
                    "PayPal-Partner-Attribution-Id": PARTNER_ATTRIBUTION_ID
                }
                data = json.dumps(data)
                url = paypal_base_url+"/v2/customer/partner-referrals"
                response = requests.post(url, data=data, headers=header)
                res_data = response.json()
                if res_data:
                    links = res_data.get("links")
                    for link in links:
                        if link.get('rel') == 'action_url':
                            return {"status": "draft", "url":link.get("href")}
        return {"status": "error", "error_msg": "Something went wrong,please ask the admin to check the payment carrier configuration!!!"}

    @http.route(['/paypal/commerce/capture/order',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_commerce_capture_order(self, **post):
        payment_provider = request.env["payment.provider"].sudo().search(
            [("code", "=", "paypal_commerce")], limit=1)
        order_id = post.get("order_id")
        if payment_provider and order_id:
            access_token = payment_provider.with_context(new_access_token=False).sudo().paypal_commerce_get_access_token()
            paypal_base_url = payment_provider.get_paypal_commerce_url()
            if access_token:
                header = {
                    "Content-Type" : "application/json",
                    "Authorization" : "Bearer " + access_token,
                    "PayPal-Partner-Attribution-Id": "Webkul_SP_SB"
                }
                url = paypal_base_url+"/v2/checkout/orders/%s/capture" % order_id
                response = requests.post(url, headers=header)
                res_data = response.json()
                if res_data.get('debug_id'):
                    return False
                else:
                    data = {}
                    seller_receivers = []
                    trnx_ref_no = ''
                    currency_code = ''
                    total_amt = 0.0
                    order_id = None
                    for p_unit in res_data.get('purchase_units'):
                        if p_unit.get('payments') and p_unit['payments'].get('captures'):
                            captures = p_unit['payments']['captures'][0]
                            amt_brkdown = captures['seller_receivable_breakdown'] if captures.get('seller_receivable_breakdown') else {}
                            if not trnx_ref_no:
                                trnx_ref_no = p_unit['reference_id'].split("/")[0] if p_unit.get('reference_id') else ''
                                if not order_id:
                                    order_ref = trnx_ref_no.split("-")[0]
                                    order = request.env["sale.order"].sudo().search([('name','=',order_ref)], limit=1)
                                    if order:
                                        order_id = order.id
                            if captures.get('amount'):
                                if not currency_code:
                                    currency_code = captures['amount']['currency_code']
                                total_amt += float(captures['amount']['value'])
                            seller_receivers.append({
                                'seller_id' : int(p_unit['reference_id'].split("/")[1]) if p_unit.get('reference_id') else None,
                                'paypal_id' : captures.get('id'),
                                'status' : captures.get('status'),
                                'order_id': order_id,
                                'currency': currency_code,
                                'is_delayed_payment' : True if captures.get('disbursement_mode') == 'DELAYED' else False,
                                'gross_amount' : float(amt_brkdown['gross_amount']['value']) if amt_brkdown.get('gross_amount') else 0.0,
                                'paypal_fee' : float(amt_brkdown['paypal_fee']['value']) if amt_brkdown.get('paypal_fee') else 0.0,
                                'platform_fees' : float(amt_brkdown['platform_fees'][0]['amount']['value']) if amt_brkdown.get('platform_fees') and amt_brkdown['platform_fees'][0].get('amount') else 0.0,
                                'net_amount' : float(amt_brkdown['net_amount']['value']) if amt_brkdown.get('net_amount') else 0.0,
                            })
                    data.update({
                        'provider_reference' : res_data.get('id'),
                        'state' : res_data.get('status'),
                        'trnx_ref_no' : trnx_ref_no,
                        'currency_code' : currency_code,
                        'total_amt' : total_amt,
                        'seller_receivers' : seller_receivers
                    })
                    request.env['payment.transaction'].sudo().form_feedback(data, 'paypal_commerce')
                    return '/payment/process'
        return False

    @http.route(['/paypal/commerce/order/validate',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_commerce_order_validate(self, **post):
        order = request.website.sale_get_order()
        marchant_ids = order.get_paypal_commerce_marchant_ids()
        provider_obj = request.env['payment.provider'].search([('code','=','paypal_commerce')], limit=1)
        if provider_obj and not provider_obj.paypal_commerce_client_id:
            return "Please configure paypal commerce client ID."
        if not marchant_ids:
            return "This payment method is not available for this order, as this order does't contain any authorized marchant product(s)."
        extra_products = []
        if order:
            for line in order.order_line:
                if not line.is_delivery:
                    seller = line.product_id.marketplace_seller_id
                    if seller:
                        if not seller.commerce_merchant_id or not seller.commerce_authorized:
                            extra_products.append(line.product_id.name)
                    else:
                        extra_products.append(line.product_id.name)
        if extra_products:
            return "Please remove these products from the cart to proceed further with this payment method: %s" % ", ".join(extra_products)
        return False

    @http.route(['/mppaypal/commerce/webhook/interface'], type='json', auth='public', csrf=False, methods=['POST'], website=True)
    def mppaypal_commerce_webhook_interface(self, **post):
        data = {}
        if request.httprequest.data:
            data = json.loads(request.httprequest.data)
            event_type = data.get('event_type')
            if event_type == 'MERCHANT.ONBOARDING.COMPLETED':
                if data.get('resource') and data['resource'].get('merchant_id'):
                    merchant_id = data['resource']['merchant_id']
                    self.update_paypal_commerce_onboard_data(merchant_id)
            if event_type == 'MERCHANT.PARTNER-CONSENT.REVOKED':
                if data.get('resource') and data['resource'].get('merchant_id'):
                    merchant_id = data['resource']['merchant_id']
                    self.remove_seller_authorization(merchant_id)
            if event_type == 'CHECKOUT.ORDER.COMPLETED':
                resource_data = data.get('resource')
                self.update_paypal_commerce_tx_data(resource_data)
            if event_type == 'PAYMENT.CAPTURE.COMPLETED':
                pass
            if event_type == 'PAYMENT.CAPTURE.DENIED':
                pass
            if event_type == 'PAYMENT.CAPTURE.REFUNDED':
                pass
            if event_type == 'PAYMENT.REFERENCED-PAYOUT-ITEM.COMPLETED':
                pass
            if event_type == 'PAYMENT.REFERENCED-PAYOUT-ITEM.FAILED':
                pass
        _logger.info("------Paypal-Commerce-Webhook-Response-----%r-------",data)
        return Response('success', status=200)
