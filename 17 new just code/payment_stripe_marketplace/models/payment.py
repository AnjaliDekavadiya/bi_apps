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

from odoo.addons.payment_stripe_marketplace.controllers.main import StripeController as MpStripeController
from odoo import models, fields, _
from odoo.addons.payment_stripe.const import STATUS_MAPPING
from odoo.addons.payment import utils as payment_utils
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

# The following currencies are integer only, see https://stripe.com/docs/currencies#zero-decimal
INT_CURRENCIES = [
    u'BIF', u'XAF', u'XPF', u'CLP', u'KMF', u'DJF', u'GNF', u'JPY', u'MGA', u'PYG', u'RWF', u'KRW',
    u'VUV', u'VND', u'XOF'
]

class PaymentProviderStripe(models.Model):
    _inherit = 'payment.provider'

    stripe_mp_client_key = fields.Char(string="Stripe Client Key", groups='base.group_user')
    is_mp_stripe = fields.Boolean(string="Marketplace Stripe")
    stripe_account_type = fields.Selection([('standard','Standard'),('express','Express')], string='Account Type', default="standard")

    def toggle_mp_stripe(self):
        for record in self:
            record.is_mp_stripe = not record.is_mp_stripe

class PaymentTransactionStripe(models.Model):
    _inherit = "payment.transaction"

    stripe_mp_receiver_ids = fields.One2many("stripe.marketplace.receiver", "tx_id", "Stripe Receivers", readonly=True)
    is_mp_stripe = fields.Boolean(related="provider_id.is_mp_stripe", string="Marketplace Stripe")

    def _get_order_amt_by_seller(self):
        self.ensure_one()
        order = self.sale_order_ids
        total_seller_amt = 0.0
        return_dict = {
            "sellers_account_amt": {},
            "sale_order": order.name if order else False,
            "admin_amt": 00.00
        }
        for sol_obj in order.order_line:
            seller_id_dict = {}
            if sol_obj.product_id.marketplace_seller_id and sol_obj.product_id.marketplace_seller_id.stripe_user_id:
                seller_obj = sol_obj.product_id.marketplace_seller_id
                amt = self.env["account.move"].sudo().calculate_commission(
                    sol_obj.price_total, seller_obj.id)
                tax_id = sol_obj.tax_id
                commission = sol_obj.price_total - amt
                if return_dict["sellers_account_amt"].get(seller_obj.id):
                    return_dict["sellers_account_amt"].get(
                        seller_obj.id)["seller_amt"] += amt
                    return_dict["sellers_account_amt"].get(
                        seller_obj.id)["admin_commission"] += commission
                else:
                    seller_id_dict.update({
                        "stripe_access_token": seller_obj.stripe_access_token,
                        "stripe_user_id": seller_obj.stripe_user_id,
                        "stripe_refresh_token": seller_obj.stripe_refresh_token,
                        "stripe_publishable_key": seller_obj.stripe_publishable_key,
                        "seller_email": seller_obj.email,
                        "seller_amt": amt,
                        "admin_commission" : commission,
                        "tax_id": tax_id,
                    })
                    return_dict["sellers_account_amt"].update(
                        {seller_obj.id: seller_id_dict})
        for seller_amt in return_dict["sellers_account_amt"].values():
            total_seller_amt += seller_amt["seller_amt"]
        return_dict["admin_amt"] = order.amount_total - total_seller_amt
        return return_dict

    def _stripe_create_payment_intent(self):
        """ Create and return a PaymentIntent.

        Note: self.ensure_one()

        :return: The Payment Intent
        :rtype: dict
        """
        if not self.token_id.stripe_payment_method:  # Pre-SCA token -> migrate it
            self.token_id._stripe_sca_migrate_customer()
        amount_dict = self._get_order_amt_by_seller()

        if amount_dict.get("sellers_account_amt") and amount_dict.get("sellers_account_amt").values():
            res = None
            #Transfer payment to all seller
            for wk_mp_dict in amount_dict.get("sellers_account_amt").values():
                response = self.provider_id._stripe_make_request(
                    'payment_intents',
                    payload={
                        'amount': payment_utils.to_minor_currency_units(self.amount, self.currency_id),
                        'currency': self.currency_id.name.lower(),
                        'confirm': True,
                        'customer': self.token_id.provider_ref,
                        'off_session': True,
                        'payment_method': self.token_id.stripe_payment_method,
                        'description': self.reference,
                        "payment_method_types[]" : 'card',
                        "transfer_data[destination]" : {wk_mp_dict.get("stripe_user_id")},
                        "receipt_email" : wk_mp_dict.get("seller_email"),
                        "application_fee_amount" : int(wk_mp_dict.get("admin_commission") * 100),
                    },
                    offline=self.operation == 'offline',
                )
                res_charge = response.get("charges").get("data")[0]
                stripe_mp_receipt_vals = {
                    "receipt_email": res_charge.get("receipt_email") and res_charge.get("receipt_email").strip(),
                    "charge_obj_id": res_charge.get("id"),
                    "balance_txn": res_charge.get("balance_transaction"),
                    "transfer": res_charge.get("transfer"),
                    "source_id": res_charge.get("source").get("id") if res_charge.get("source") else False,
                    "is_paid": "Yes" if res_charge.get("paid") else "No",
                    "status": res_charge.get("status"),
                    "destination_acc_id": response['transfer_data'].get('destination') if res_charge.get('transfer_data') else '',
                    "amount": format(float(res_charge.get("amount") / 100.00), '.2f') if res_charge.get("amount") else 0.00,
                    "currency": res_charge.get("currency"),
                    "stripe_response": response,
                    "tx_id": self.id
                }
                self.env["stripe.marketplace.receiver"].sudo().create(stripe_mp_receipt_vals)

        else:
            response = self.provider_id._stripe_make_request(
                'payment_intents',
                payload={
                    'amount': payment_utils.to_minor_currency_units(self.amount, self.currency_id),
                    'currency': self.currency_id.name.lower(),
                    'confirm': True,
                    'customer': self.token_id.provider_ref,
                    'off_session': True,
                    'payment_method': self.token_id.stripe_payment_method,
                    'description': self.reference,
                },
                offline=self.operation == 'offline',
            )
            res_charge = response.get("charges").get("data")[0]
            stripe_mp_receipt_vals = {
                "receipt_email": res_charge.get("receipt_email") and res_charge.get("receipt_email").strip(),
                "charge_obj_id": res_charge.get("id"),
                "balance_txn": res_charge.get("balance_transaction"),
                "transfer": res_charge.get("transfer"),
                "source_id": res_charge.get("source").get("id") if res_charge.get("source") else False,
                "is_paid": "Yes" if res_charge.get("paid") else "No",
                "status": res_charge.get("status"),
                "destination_acc_id": res_charge.get("destination"),
                "amount": format(float(res_charge.get("amount") / 100.00), '.2f') if res_charge.get("amount") else 0.00,
                "currency": res_charge.get("currency"),
                "stripe_response": response,
                "tx_id": self.id
            }
            self.env["stripe.marketplace.receiver"].sudo().create(stripe_mp_receipt_vals)
        if 'error' not in response:
            payment_intent = response
        else:  # A processing error was returned in place of the payment intent
            error_msg = response['error'].get('message')
            self._set_error("Stripe: " + _(
                "The communication with the API failed.\n"
                "Stripe gave us the following info about the problem:\n'%s'", error_msg
            ))  # Flag transaction as in error now as the intent status might have a valid value
            payment_intent = response['error'].get('payment_intent')  # Get the PI from the error

        return payment_intent

    def _process_notification_data(self, data):
        """ Override of payment to process the transaction based on Adyen data.

        Note: self.ensure_one()

        :param dict data: The feedback data build from information passed to the return route.
                          Depending on the operation of the transaction, the entries with the keys
                          'payment_intent', 'charge', 'setup_intent' and 'payment_method' can be
                          populated with their corresponding Stripe API objects.
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(data)
        if self.provider_code != 'stripe':
            return
        if self.operation == 'validation':
            intent_status = data.get('setup_intent', {}).get('status')
        else:  # 'online_redirect', 'online_token', 'offline'
            intent_status = data.get('payment_intent', {}).get('status')
        if not intent_status:
            raise ValidationError(
                "Stripe: " + _("Received data with missing intent status.")
            )
        if intent_status in STATUS_MAPPING['done']:
            self.stripe_mp_create_seller_order_paid_payment()

    def stripe_mp_create_seller_order_paid_payment(self):
        self.ensure_one()
        for sale_order_id in self.sale_order_ids:
            if sale_order_id:
                seller_amount_dict = self._get_order_amt_by_seller()
                stripe_payment_method = self.env.ref('payment_stripe_marketplace.marketplace_seller_payment_method_data7_stripe_mp').id
                for wk_mp_dict in seller_amount_dict.get("sellers_account_amt"):
                    invoice_currency = self.currency_id
                    invoice_amount = seller_amount_dict.get("sellers_account_amt").get(wk_mp_dict).get("seller_amt")
                    mp_currency_id = self.env['res.config.settings'].get_mp_global_field_value("mp_currency_id")
                    mp_currency_obj = self.env["res.currency"].browse(mp_currency_id)
                    amount = invoice_currency._convert(invoice_amount, mp_currency_obj)
                    seller_payment_obj = self.env['seller.payment'].sudo().with_context(pass_create_validation=True).create({
                        "seller_id": wk_mp_dict,
                        "payment_method": stripe_payment_method,
                        "payment_mode": "seller_payment",
                        "description": _("Seller requested for payment..."),
                        "payment_type": "dr",
                        "state": "requested",
                        "memo":seller_amount_dict.get("sale_order"),
                        "payable_amount": amount,
                        })
                    if seller_payment_obj:
                        seller_payment_obj.sudo().do_Confirm()
                        MpStripeController()._generate_and_pay_seller_payment_by_sripe_mp(self, seller_payment_obj.invoice_id)

class StripeMarketplaceReceiver(models.Model):
    _name = "stripe.marketplace.receiver"
    _description = "Stripe Marketplace Receiver"
    _rec_name = "receipt_email"

    receipt_email = fields.Char("Email")
    charge_obj_id = fields.Char("Source Txn")
    balance_txn = fields.Char("")
    transfer = fields.Char("Transfer")
    source_id = fields.Char("Source Id")
    is_paid = fields.Char("Paid")
    status = fields.Char("Status")
    destination_acc_id = fields.Char("Destination A/C Id")
    amount = fields.Char("Amount")
    currency = fields.Char("Currency")
    stripe_response = fields.Text("Stripe Response")
    tx_id = fields.Many2one("payment.transaction", "Payment Tx")

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_onboard_seller_ids(self):
        self.ensure_one()
        sellers = self.order_line.mapped('product_id').mapped('marketplace_seller_id')
        onboard_seller_ids = sellers.filtered(lambda sel: sel.stripe_user_id and sel.stripe_access_token)
        return onboard_seller_ids
