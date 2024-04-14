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
from odoo import api, http, tools, _
from odoo.http import request, Response
from odoo.addons.payment_paypal_express.controllers.main import PaypalExpressRedirect
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.payment.controllers.portal import PaymentPortal
from datetime import datetime, timedelta
from odoo.tools import float_repr
import hashlib
import hmac
from odoo.tools import consteq
from odoo.tools.misc import ustr
import requests
import json
import werkzeug

import logging
_logger = logging.getLogger(__name__)

class PaypalReccuring(PaypalExpressRedirect):

    @http.route(['/paypal/express/checkout/url',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_url(self, **post):
        provider_obj = request.env['payment.provider'].sudo().search([('code','=','paypal_express')], limit=1)
        if not provider_obj:
            return False
        order = request.website.sale_get_order()
        if order:
            sub_lines = order.order_line.filtered(lambda line: line.product_id and line.product_id.activate_subscription and line.product_id.subscription_plan_id)
            if sub_lines:
                url = "https://www.paypal.com/sdk/js?client-id=" + str(provider_obj.paypal_client_id) + "&vault=true&intent=subscription"
                pricelist = request.session.get('website_sale_current_pl')
                lang = request.lang
                if pricelist:
                    pricelist = request.env['product.pricelist'].browse(pricelist)
                    if pricelist and pricelist.currency_id:
                        url += '&currency=' + str(pricelist.currency_id.name)
                if lang:
                    url += '&locale=' + str(lang.code)
                return {
                    "type": "recurring",
                    "url": url
                }
        url = super(PaypalReccuring, self).paypal_checkout_checkout_url(**post)
        return {
            "type": "express",
            "url": url
        }

    @http.route(['/paypal/express/checkout/state',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_state(self, **post):
        if post.get('subscription_id'):
            subscription_id = post.get('subscription_id')
            order = request.website.sale_get_order()
            if order:
                order.action_confirm()
                sub_obj = order.subscription_ids
                if sub_obj:
                    sub_obj = sub_obj[0]
                    sub_obj.paypal_sub = True
                    sub_obj.subscription_ref = subscription_id
                trans_id = request.session.get('__website_sale_last_tx_id',False)
                if trans_id:
                    trans_obj = request.env['payment.transaction'].sudo().browse(int(trans_id)) if trans_id else None
                    try:
                        if sub_obj and sub_obj.trial_period:
                            trans_obj.amount = 0.00001
                            trans_obj._set_done()
                        else:
                            trans_obj._set_pending()
                            if sub_obj:
                                trans_obj.paypal_sub_id = sub_obj.id
                    except Exception as e:
                        _logger.info("~~~~~~~~Transaction already in process~~~~~~~~~")
            return '/payment/state'
        else:
            return super(PaypalReccuring, self).paypal_checkout_checkout_state(**post)

    @http.route(['/paypal/recurring/order/validate',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_recurring_order_validate(self, **post):
        order = request.website.sale_get_order()
        provider_obj = request.env['payment.provider'].sudo().search([('code','=','paypal_express')], limit=1)
        if provider_obj:
            if not provider_obj.paypal_client_id:
                return "Please ask the admin to configure PayPal Client ID in payment provider."
            elif not provider_obj.paypal_secret_id:
                return "Please ask the admin to configure PayPal Secret ID in payment provider."
            elif (provider_obj.state == 'enabled' and not provider_obj.paypal_recurring_webhook_id) or (provider_obj.state != 'enabled' and not provider_obj.sb_paypal_recurring_webhook_id):
                return "Please ask the admin to register the PayPal Webhook in payment provider."
        if order:
            sub_lines = order.order_line.filtered(lambda line: line.product_id and line.product_id.activate_subscription and line.product_id.subscription_plan_id)
            if not sub_lines:
                return False
            elif len(order.order_line) > 1:
                return "This payment method only supports either subscription product(Only one subscription in a single go) or non-subscription products."
            elif len(sub_lines) != 1:
                return "Order contains more than one subscription product, only one is allowed for this payment method."
            else:
                return False
        return False

    def create_plan_on_paypal(product_id, line):
        payment_provider = request.env["payment.provider"].sudo().search([("code", "=", "paypal_express")], limit=1)
        access_token = payment_provider.sudo().paypal_recurring_get_access_token()
        paypal_base_url = payment_provider.get_paypal_recurring_base_url()
        header = {
            "Content-Type" : "application/json",
            "Authorization" : "Bearer " + access_token,
        }
        data = {
            "name": product_id.name,
            "type": "SERVICE"
        }
        if product_id.description:
            data["description"] = product_id.description
        data = json.dumps(data)
        url = paypal_base_url + "/v1/catalogs/products"
        response = requests.post(url, data=data, headers=header)
        res_data = response.json()
        if res_data.get('id'):
            plan = product_id.subscription_plan_id
            data = {
                "product_id": res_data['id'],
                "name": plan.name,
                "description": plan.plan_description,
                "status": "ACTIVE",
                "billing_cycles": [],
                "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "setup_fee_failure_action": "CONTINUE",
                    "payment_failure_threshold": 3
                }
            }
            valid_trial = False

            if plan.trial_period:
                trial_period_setting = request.env['res.config.settings'].sudo().get_values()['trial_period_setting']
                partner_id = request.env.user.partner_id
                if trial_period_setting=='one_time' and not len(partner_id.sudo().all_subscription)!=0 or trial_period_setting=='product_based' and not partner_id.sudo().all_subscription.filtered(lambda subscription:subscription.product_id==line.sudo().product_id):
                    data["billing_cycles"].append({
                      "frequency": {
                        "interval_unit": plan.trial_duration_unit,
                        "interval_count": plan.trial_duration
                      },
                      "tenure_type": "TRIAL",
                      "sequence": 1,
                      "total_cycles": 1
                    })
                    valid_trial = True
            data["billing_cycles"].append({
                "frequency": {
                    "interval_unit": plan.unit,
                    "interval_count": plan.duration
                },
                "tenure_type": "REGULAR",
                "sequence": 2 if valid_trial else 1,
                "total_cycles": 0 if plan.never_expires else plan.num_billing_cycle,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": line.price_unit,
                        "currency_code": line.currency_id.name
                    }
                }
            })
            data = json.dumps(data)
            url = paypal_base_url + "/v1/billing/plans"
            response = requests.post(url, data=data, headers=header)
            res_data = response.json()
            if res_data.get('id'):
                return res_data['id']
        return False

    def activate_paypal_subscription(sub_id):
        paypal_sub_id = sub_id.subscription_ref
        if sub_id.paypal_sub and paypal_sub_id:
            payment_provider = request.env["payment.provider"].sudo().search([("code", "=", "paypal_express")], limit=1)
            access_token = payment_provider.sudo().paypal_recurring_get_access_token()
            paypal_base_url = payment_provider.get_paypal_recurring_base_url()
            header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + access_token,
            }
            url = paypal_base_url + "/v1/billing/subscriptions/" + paypal_sub_id + "/activate"
            response = requests.post(url, headers=header)
        pass

    def suspend_paypal_subscription(sub_id):
        paypal_sub_id = sub_id.subscription_ref
        if sub_id.paypal_sub and paypal_sub_id:
            payment_provider = request.env["payment.provider"].sudo().search([("code", "=", "paypal_express")], limit=1)
            access_token = payment_provider.sudo().paypal_recurring_get_access_token()
            paypal_base_url = payment_provider.get_paypal_recurring_base_url()
            header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + access_token,
            }
            url = paypal_base_url + "/v1/billing/subscriptions/" + paypal_sub_id + "/suspend"
            response = requests.post(url, headers=header)
        pass

    def cancel_paypal_subscription(sub_id):
        paypal_sub_id = sub_id.subscription_ref
        if sub_id.paypal_sub and paypal_sub_id:
            payment_provider = request.env["payment.provider"].sudo().search([("code", "=", "paypal_express")], limit=1)
            access_token = payment_provider.sudo().paypal_recurring_get_access_token()
            paypal_base_url = payment_provider.get_paypal_recurring_base_url()
            header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + access_token,
            }
            url = paypal_base_url + "/v1/billing/subscriptions/" + paypal_sub_id + "/cancel"
            response = requests.post(url, headers=header)
        pass

    def paypal_recurring_update_access_token(provider_id):
        data = {
            "grant_type" : "client_credentials"
        }
        auth = (provider_id.paypal_client_id, provider_id.paypal_secret_id)
        paypal_base_url = provider_id.get_paypal_recurring_base_url()
        url = paypal_base_url+"/v1/oauth2/token"
        response = requests.post(url, params=data, auth=auth)
        res_data = response.json()
        if res_data:
            provider_id.paypal_recurring_access_token = res_data.get('access_token')
            expires_in = res_data.get('expires_in')
            if expires_in:
                provider_id.paypal_recurring_expiry_date = datetime.now() + timedelta(seconds=expires_in)
        return

    def registered_paypal_recurring_webhook(provider_id):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        access_token = provider_id.sudo().paypal_recurring_get_access_token()
        paypal_base_url = provider_id.get_paypal_recurring_base_url()
        if access_token:
            header = {
                "Content-Type" : "application/json",
                "Authorization" : "Bearer " + access_token,
            }
            data = {
                "url": base_url+"/paypal/recurring/webhook/interface",
                "event_types": [
                    {"name": "BILLING.SUBSCRIPTION.ACTIVATED"},
                    {"name": "BILLING.SUBSCRIPTION.UPDATED"},
                    {"name": "BILLING.SUBSCRIPTION.SUSPENDED"},
                    {"name": "BILLING.SUBSCRIPTION.CANCELLED"},
                    {"name": "PAYMENT.SALE.COMPLETED"}
                ]
            }
            data = json.dumps(data)
            url = paypal_base_url+"/v1/notifications/webhooks"
            response = requests.post(url, data=data, headers=header)
            res_data = response.json()
            if res_data:
                webhook_id = res_data.get("id")
                if webhook_id:
                    if provider_id.state == 'enabled':
                        provider_id.write({"paypal_recurring_webhook_id": webhook_id})
                    else:
                        provider_id.write({"sb_paypal_recurring_webhook_id": webhook_id})
                elif res_data.get("message"):
                    return res_data["message"]
        return None

    def delete_registed_paypal_recurring_webhook(provider_id):
        access_token = provider_id.sudo().paypal_recurring_get_access_token()
        paypal_base_url = provider_id.get_paypal_recurring_base_url()
        provider_obj = request.env['payment.provider'].sudo().search([('code','=','paypal_express')], limit=1)
        header = {
            "Content-Type" : "application/json",
            "Authorization" : "Bearer " + access_token,
        }
        webhook_id = provider_obj.paypal_recurring_webhook_id if provider_obj.state == 'enabled' else provider_obj.sb_paypal_recurring_webhook_id
        if webhook_id:
            url = paypal_base_url + "/v1/notifications/webhooks/" + webhook_id
            response = requests.delete(url, headers=header)
            res_data = response.json()

    @http.route(['/paypal/recurring/webhook/interface'], type='json', auth='public', csrf=False, methods=['POST'], website=True)
    def paypal_recurring_webhook_interface(self, **post):
        data = {}
        if request.httprequest.data:
            data = json.loads(request.httprequest.data)
            event_type = data.get('event_type')
            if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
                pass
            if event_type == 'BILLING.SUBSCRIPTION.UPDATED':
                pass
            if event_type == 'BILLING.SUBSCRIPTION.SUSPENDED':
                pass
            if event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
                pass
            if event_type == 'PAYMENT.SALE.COMPLETED':
                resource = data.get('resource')
                if resource:
                    sub_ref = resource['billing_agreement_id']
                    subscription_id = request.env['subscription.subscription'].sudo().search([('subscription_ref','=',sub_ref)], limit=1)
                    if subscription_id:
                        tx_id = subscription_id.paypal_sub_tx_ids.filtered(lambda tx: tx.state == 'pending')
                        if tx_id:
                            tx_id.acquirer_reference = data.get('id')
                            if resource.get('state') and resource['state'] == 'completed':
                                tx_id.sudo()._set_transaction_done()
                        else:
                            params = {
                                'acq_ref': data.get('id'),
                                'sub_id': resource.get('billing_agreement_id'),
                                'state': resource.get('state')
                            }
                            subscription_id.sudo()._create_paypal_recurring_payment(params)
        return Response('success', status=200)

class WebsitePayment(PaymentPortal):


    @http.route('/payment/confirmation', type='http', methods=['GET'], auth='public', website=True)
    def payment_confirm(self, tx_id, access_token, **kwargs):
        tx_id = self._cast_as_int(tx_id)
        if tx_id:
            tx_sudo = request.env['payment.transaction'].sudo().browse(tx_id)

            # Raise an HTTP 404 if the access token is invalid
            if not payment_utils.check_access_token(
                access_token, tx_sudo.partner_id.id, tx_sudo.amount, tx_sudo.currency_id.id
            ):
                raise werkzeug.exceptions.NotFound()  # Don't leak information about ids.

            # Stop monitoring the transaction now that it reached a final state.
            PaymentPostProcessing.remove_transactions(tx_sudo)

            # Display the payment confirmation page to the user
            return request.render('payment.confirm', qcontext={'tx': tx_sudo})
        else:
            # Display the portal homepage to the user
            return request.redirect('/my/home')
