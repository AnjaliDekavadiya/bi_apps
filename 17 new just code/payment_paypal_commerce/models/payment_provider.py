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
import pprint
from odoo import api, models, fields, _
from odoo.addons.payment_paypal_commerce.controllers.main import PaypalCommerceController as PC
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('paypal_commerce', 'Paypal Commerce')], ondelete={'paypal_commerce': 'set default'})
    paypal_commerce_access_token = fields.Char("Paypal Commerce Access Token")
    paypal_commerce_expiry_date = fields.Datetime("Token Expiry Date")
    paypal_commerce_client_id = fields.Char("Client ID")
    paypal_commerce_secret_id = fields.Char("Secret ID")
    paypal_merchant_id = fields.Char("Merchant ID")
    paypal_partner_attribution_id = fields.Char("Partner Attribution ID", default="Webkul_SP_SB")
    paypal_commerce_webhook_id = fields.Char("Webhook ID")
    paypal_commerce_delay_payment = fields.Boolean("Delayed Payment")

    def get_paypal_commerce_url(self):
        self.ensure_one()
        if self.state == 'enabled':
            return "https://api.paypal.com"
        else:
            return "https://api.sandbox.paypal.com"

    def registered_paypal_commerce_webhook(self):
        return PC.registered_mppaypal_commerce_webhook(self)

    def paypal_commerce_get_access_token(self):
        self.ensure_one()
        if self._context.get('new_access_token') or not self.paypal_commerce_access_token or datetime.now() >= self.paypal_commerce_expiry_date:
            PC.paypal_commerce_update_access_token(self)
        if self.paypal_commerce_access_token:
            return self.paypal_commerce_access_token
        else:
            return ''

class PaypalCommerceMpReceiver(models.Model):
    _name = "paypal.commerce.mp.receiver"
    _description = "Paypal Commerce Mp Receiver"

    gross_amount = fields.Float("Gross Amount")
    paypal_fee = fields.Float("Paypal Fee")
    platform_fees = fields.Float("Platform Fee")
    net_amount = fields.Float("Received Amount")
    currency = fields.Char("Currency")
    paypal_id = fields.Char("Transaction ID")
    seller_id = fields.Many2one("res.partner", string="Seller")
    order_id = fields.Many2one("sale.order", string="Sale Order")
    is_delayed_payment = fields.Boolean("Delayed Payment")
    status = fields.Char("Status")
    tx_id = fields.Many2one("payment.transaction", "Payment Tx")
    is_refunded = fields.Boolean("Refunded")
    refund_status = fields.Char("Refund Status")
    refund_id = fields.Char("Refund ID")
    is_released = fields.Boolean("Released")
    released_status = fields.Char("Released Status")
    seller_payment_id = fields.Many2one("seller.payment", string="Seller Payment")

    def paypal_commerce_refund_order(self):
        refund_data = PC.paypal_commerce_refund_order(self.tx_id.provider_id, self.paypal_id, self.seller_id.commerce_merchant_id)
        if refund_data:
            if refund_data.get('error_msg'):
                assert False, refund_data["error_msg"]
            else:
                self.sudo().write(refund_data)

    def _create_paypal_commerce_seller_payments(self):
        if self.seller_payment_id:
            return
        paypal_comm_payment_method = self.env.ref('payment_paypal_commerce.marketplace_seller_payment_method_mp_paypal_comm').id
        vals = {
            "seller_id": self.seller_id.id,
            "payment_method": paypal_comm_payment_method,
            "payment_mode": "seller_payment",
            "description": _("Seller requested for payment..."),
            "payment_type": "dr",
            "state": "requested",
            "payable_amount": self.net_amount+self.paypal_fee,
        }
        seller_payment_obj = self.env['seller.payment'].sudo().with_context(pass_create_validation=True).create(vals)
        if seller_payment_obj:
            self.seller_payment_id = seller_payment_obj
            seller_payment_obj.sudo().do_Confirm()
            seller_bill = seller_payment_obj.invoice_id
            if seller_bill:
                try:
                    seller_bill.action_invoice_open()
                except Exception as e:
                    _logger.warning("Can not perform invoice open action on seller bill.")
                seller_journal_id = self.env['res.config.settings'].get_mp_global_field_value("seller_payment_journal_id")
                journal_obj = self.env["account.journal"].sudo().browse(seller_journal_id)
                if journal_obj:
                    seller_bill.post()

    def paypal_commerce_release_seller_payment(self):
        released_data = PC.paypal_commerce_release_seller_payment(self.tx_id.provider_id, self.paypal_id)
        if released_data:
            if released_data.get('error_msg'):
                assert False, released_data["error_msg"]
            else:
                self.sudo().write(released_data)

    @api.model_create_multi
    def create(self, vals_list):
        result = super(PaypalCommerceMpReceiver, self).create(vals_list)
        for res in result:
            if res.status == 'COMPLETED':
                res._create_paypal_commerce_seller_payments()
        return result

    def write(self, vals):
        res = super(PaypalCommerceMpReceiver, self).write(vals)
        if vals.get('status') and vals['status'] == 'COMPLETED':
            for record in self:
                record._create_paypal_commerce_seller_payments()
        return res

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_paypal_commerce_marchant_ids(self):
        self.ensure_one()
        sellers = self.order_line.mapped('product_id').mapped('marketplace_seller_id')
        marchant_ids = sellers.filtered(lambda sel: sel.commerce_merchant_id and sel.commerce_authorized).mapped('commerce_merchant_id')
        return marchant_ids
