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
from odoo.addons.payment_paypal_recurring.controllers.main import PaypalReccuring as PR
from odoo.exceptions import UserError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    paypal_secret_id = fields.Char("PayPal Secret ID", required_if_provider='paypal_express', help="Enter PayPal Secret ID.")
    paypal_recurring_access_token = fields.Char("PayPal Recurring Access Token")
    paypal_recurring_expiry_date = fields.Datetime("Token Expiry Date")
    paypal_recurring_webhook_id = fields.Char("Webhook ID")
    sb_paypal_recurring_webhook_id = fields.Char("Webhook ID")

    def paypal_express_form_generate_values(self, values):
        vals = super(PaymentProvider, self).paypal_express_form_generate_values(values)
        reference = values.get('reference')
        vals["plan_id"] = False
        if reference:
            order_name = reference.split('-')[0]
            order = self.env['sale.order'].search([('name','=',order_name)], limit=1)
            sub_lines = order.order_line.filtered(lambda line: line.product_id and line.product_id.activate_subscription and line.product_id.subscription_plan_id)
            if sub_lines and len(order.order_line) == 1:
                sub_lines = sub_lines[0]
                plan_id =  PR.create_plan_on_paypal(sub_lines.product_id, sub_lines)
                trial_period_setting = self.env['res.config.settings'].sudo().get_values()['trial_period_setting']
                partner_id = self.env["res.partner"].sudo().browse(vals.get('partner_id'))

                if plan_id:
                    vals["plan_id"] = plan_id
                    plan = sub_lines.product_id.subscription_plan_id
                    if plan and plan.trial_period:
                        sub_amount = vals['amount']
                        vals['amount'] = 0.0
                        if trial_period_setting=='one_time' and len(partner_id.all_subscription)!=0:
                            vals['amount'] = sub_amount
                        elif trial_period_setting=='product_based' and partner_id.all_subscription.filtered(lambda subscription:subscription.product_id==sub_lines.product_id):
                            vals['amount'] = sub_amount
        return vals

    def get_paypal_recurring_base_url(self):
        self.ensure_one()
        return "https://api-m.paypal.com" if self.state == 'enabled' else "https://api-m.sandbox.paypal.com"

    def paypal_recurring_get_access_token(self):
        self.ensure_one()
        if self._context.get('new_access_token') or not self.paypal_recurring_access_token or datetime.now() >= self.paypal_recurring_expiry_date:
            PR.paypal_recurring_update_access_token(self)
        if self.paypal_recurring_access_token:
            return self.paypal_recurring_access_token
        else:
            return False

    def registered_paypal_recurring_webhook(self):
        msg = PR.registered_paypal_recurring_webhook(self)
        if msg:
            raise UserError(_(msg))

class TransactionPaypalExpress(models.Model):
    _inherit = 'payment.transaction'

    paypal_sub_id = fields.Many2one('subscription.subscription', "Subscription")

    def _get_specific_rendering_values(self, processing_values):
        vals = super()._get_specific_rendering_values(processing_values)
        reference = processing_values.get('reference')
        vals["plan_id"] = False
        if reference:
            order_name = reference.split('-')[0]
            order = self.env['sale.order'].search([('name','=',order_name)], limit=1)
            sub_lines = order.order_line.filtered(lambda line: line.product_id and line.product_id.activate_subscription and line.product_id.subscription_plan_id)
            if sub_lines and len(order.order_line) == 1:
                sub_lines = sub_lines[0]
                plan_id =  PR.create_plan_on_paypal(sub_lines.product_id, sub_lines)
                trial_period_setting = self.env['res.config.settings'].sudo().get_values()['trial_period_setting']
                partner_id = self.env["res.partner"].sudo().browse(vals.get('partner_id'))

                if plan_id:
                    vals["plan_id"] = plan_id
                    plan = sub_lines.product_id.subscription_plan_id
                    if plan and plan.trial_period:
                        sub_amount = vals['amount']
                        vals['amount'] = 0.0
                        if trial_period_setting=='one_time' and len(partner_id.all_subscription)!=0:
                            vals['amount'] = sub_amount
                        elif trial_period_setting=='product_based' and partner_id.all_subscription.filtered(lambda subscription:subscription.product_id==sub_lines.product_id):
                            vals['amount'] = sub_amount
        return vals
