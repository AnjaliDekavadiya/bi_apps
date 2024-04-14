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

import datetime
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class SubscriptionSubscription(models.Model):
    _inherit = "subscription.subscription"

    paypal_sub = fields.Boolean("PayPal Subscription")
    paypal_sub_tx_ids = fields.One2many('payment.transaction','paypal_sub_id','PayPal Recurring Payment Reference')

    def action_invoice_create(self, grouped=False, final=False):
        rec = self.filtered(lambda sub: not sub.paypal_sub)
        return super(SubscriptionSubscription, rec).action_invoice_create(grouped=grouped, final=final)

    def _create_paypal_recurring_payment(self, data):
        if self.paypal_sub and data:
            inv_data = self._prepare_invoice()
            invoice_lines = self.invoice_line_create(inv_data, self.quantity)
            invoice = self.env['account.move'].create(invoice_lines)
            if invoice:
                sent_invoice = self.env["ir.default"].get('res.config.settings', 'invoice_email')
                if self.invoice_ids:
                    self.invoice_ids =  [(4, invoice.id)]
                else:
                    self.invoice_ids = [invoice.id]
                # need to create tx over here
                provider_id = self.env['payment.provider'].sudo().search([('code','=','paypal_express')], limit=1)
                order_id = self.so_origin
                reference_values = order_id and {'sale_order_ids': [(4, order_id)]} or {}
                reference = self.env['payment.transaction']._compute_reference(values=reference_values, prefix=self.name)
                values = {
                    'provider_id': int(provider_id),
                    'provider_reference': data.get('acq_ref'),
                    'paypal_sub_id': self.id,
                    'reference': reference,
                    'return_url': '/shop/payment/validate',
                }
                tx_id =  invoice and invoice._create_payment_transaction(values) or False
                if data.get('state') and data['state'] == 'completed':
                    tx_id._set_transaction_done()
                self.paypal_settle_invoice(invoice, sent_invoice, state="paid")
                start_date = datetime(year=self.start_date.year, month=self.start_date.month, day=self.start_date.day, minute=0, hour=0, second=0) if self.source =='manual' else self.start_date + relativedelta(days = 1)
                if not isinstance(start_date, datetime):
                    start_date = datetime(*start_date.timetuple()[:6])
                if self.num_billing_cycle != self.invoice_count:
                    if self.num_billing_cycle>0:
                        end_date = datetime(year=self.end_date.year, month=self.end_date.month, day=self.end_date.day, minute=0, hour=0, second=0)
                        date_intervals = self.cal_date_period(start_date, end_date, self.num_billing_cycle)
                        self.next_payment_date = datetime.strptime(date_intervals[self.invoice_count-1],"%d/%m/%Y %H:%M:%S")
                    else:
                        end_date = start_date if not self.next_payment_date else self.next_payment_date
                        if self.unit == 'day':
                            end_date = end_date  + relativedelta(days = self.duration)
                        if self.unit == 'month':
                            end_date = end_date + relativedelta(months = self.duration)
                        if self.unit == 'year':
                            end_date = end_date + relativedelta(years = self.duration)
                        if self.unit == 'week':
                            end_date = end_date + timedelta(weeks = self.duration)
                        self.next_payment_date = end_date
                else:
                    self.next_payment_date = self.end_date

    def paypal_settle_invoice(self, invoice, sent_invoice, state='post'):
        invoice.make_payment(state)
        message = state + "Post Invoice Created"
        if sent_invoice:
            template = self.env.ref('account.email_template_edi_invoice')
            subjects = self.env['mail.template']._render_template(template.subject, 'account.move', invoice.id)
            body = template._render_template(template.body_html, 'account.move', invoice.id)
            emails_from = self.env['mail.template']._render_template(template.email_from,'account.move', invoice.id)
            mail_compose_obj = self.env['mail.compose.message'].create({
                'subject':subjects,
                'body':body,
                'parent_id':False,
                'email_from':emails_from,
                'model':'account.move',
                'res_id':invoice.id,
                'record_name':invoice.name,
                'message_type':'comment',
                'composition_mode':'comment',
                'partner_ids':[invoice.partner_id.id],
                'auto_delete':False,
                'template_id':template.id,
                'add_sign':True,
                'subtype_id':1,
                'author_id':self.env.user.partner_id.id,
            })
            mail_compose_obj.with_context(custom_layout="mail.mail_notification_paynow",model_description='invoice').send_mail()
            self.mapped('invoice_ids').write({'invoice_sent': True})
