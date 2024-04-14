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
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment_paypal_commerce.controllers.main import PaypalCommerceController as PC
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    paypal_commerce_receiver_ids = fields.One2many("paypal.commerce.mp.receiver", "tx_id", "Paypal Commerce Receivers", readonly=True)

    def _create_paypal_commerce_order(self, values):
        return PC.paypal_commerce_create_order(self, values)

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'paypal_commerce':
            return res
        base_url = self.get_base_url()
        tx_values = dict(processing_values)
        vals = {
            'order' : tx_values.get('order'),
            'amount': self.amount,
            'currency_code': self.currency_id.name,
            'reference' : self.reference
        }
        tx_values.update({
            'commerce_order_id': self._create_paypal_commerce_order(vals)
        })
        return tx_values

    # def render_sale_button(self, order, submit_txt=None, render_values=None):
    #     if render_values:
    #         render_values['order'] = order
    #     else:
    #         render_values = {'order':order}
    #     return super(PaymentTransaction, self).render_sale_button(order, submit_txt=submit_txt, render_values=render_values)

    @api.model
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Given a data dict coming from thawani, verify it and find the related
        transaction record. Create a payment method if an alias is returned."""
        res = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "paypal_commerce":
            return res
        reference = notification_data.get('trnx_ref_no')
        tx_ids = None
        provider_reference = notification_data.get('provider_reference')
        if reference:
            tx_ids = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not tx_ids and provider_reference:
            tx_ids = self.env['payment.transaction'].search([('provider_reference', '=', provider_reference)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'received data for reference %s' % (pprint.pformat(reference))
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx_ids[0]

    def _create_paypal_commerce_receivers(self, seller_receivers):
        for reciver in seller_receivers:
            reciver['tx_id'] = self.id
            self.env["paypal.commerce.mp.receiver"].sudo().create(reciver)

    def _update_paypal_commerce_receivers(self, update_receivers):
        for reciver in update_receivers:
            receiver_obj = self.paypal_commerce_receiver_ids.filtered(lambda l: l.paypal_id == reciver['paypal_id'])
            receiver_obj.sudo().write({'status':reciver['status']})

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != "paypal_commerce":
            return
        trans_state = notification_data.get("state", False)
        if notification_data.get('seller_receivers'):
            self._create_paypal_commerce_receivers(notification_data['seller_receivers'])
        if notification_data.get('update_receivers'):
            self._update_paypal_commerce_receivers(notification_data['update_receivers'])
        if trans_state:
            vals = {'state_message': _("Paypal Payment Gateway Response :-") + notification_data["state"]}
            if notification_data.get('provider_reference'):
                vals['provider_reference'] = notification_data['provider_reference']
            self.write(vals)
            if trans_state == 'COMPLETED':
                self._set_done()
            elif trans_state == "PENDING":
                self._set_pending()
            elif trans_state == "DECLINED":
                self._set_canceled()
            # elif trans_state == "PARTIALLY_REFUNDED":
            # elif trans_state == "REFUNDED":
