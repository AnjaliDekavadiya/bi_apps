# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class SendWAMessage(models.TransientModel):
    _inherit = 'whatsapp.msg'

    @api.model
    def default_get(self, fields):
        result = super(SendWAMessage, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        if not active_model or active_model == 'pos.order':
            return result
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        msg = result.get('message', '')

        # Sale Order
        if active_model == 'sale.order':
            doc_name = 'quotation' if rec.state in ('draft', 'sent') else 'order'
            msg = "Hello,"
            msg += "\n\nYour "
            tx_sudo = rec.get_portal_last_transaction()
            if rec.state == 'sale' or (tx_sudo and tx_sudo.state in ('done', 'authorized')):
                msg += "order amounting in *" + self.format_amount(rec.amount_total, rec.currency_id) + "*"
                msg += " has been confirmed.\nThank you for your trust!"
            elif tx_sudo and tx_sudo.state == 'pending':
                msg += "order amounting in *" + self.format_amount(rec.amount_total, rec.currency_id) + "*"
                msg += " is pending. It will be confirmed when the payment is received."
                if rec.reference:
                    msg += "Your payment reference is *" + rec.reference + "*"
            else:
                if self.env.context.get('proforma'):
                    msg += "Pro forma invoice for " + doc_name + " *" + rec.name + "* "
                    if rec.origin:
                        msg += "(with reference: " + rec.origin + ")"
                    msg += " amounting in *" + self.format_amount(rec.amount_total, rec.currency_id) + "*  is available."
                else:
                    msg += doc_name + " *" + rec.name + "* "
                    if rec.origin:
                        msg += "(with reference: " + rec.origin + ")"
                    msg += " amounting in *" + self.format_amount(rec.amount_total, rec.currency_id) + "* is ready for review."
            msg += "\n\n"
            msg += "Do not hesitate to contact us if you have any questions."
            if rec.user_id.signature:
                msg += "\n\n*" + html2plaintext(rec.user_id.signature) + "*"

        # Purchase Order
        if active_model == 'purchase.order':
            doc_name = _('Request for Quotation') if rec.state in ['draft', 'sent'] else _('Purchase Order')
            msg = "Dear *PARTNER*" \
            "\nHere is in attachment a " + doc_name + " *" + rec.name + "*"
            if rec.partner_ref:
                msg += " with reference: " + rec.partner_ref
            if rec.state == 'purchase':
                msg += " amounting in *" + self.format_amount(rec.amount_total, rec.currency_id) + "*"
            msg += " from " + rec.company_id.name + ".\n\n"
            msg += "If you have any questions, please do not hesitate to contact us.\n\n" \
            "Best regards."

        # Stock Picking (Delivery)
        if active_model == 'stock.picking':
            msg = "Hello *PARTNER*"\
            "\n\nWe are glad to inform you that your order has been shipped."
            if rec.carrier_tracking_ref:
                msg += "Your tracking reference is *"
                if rec.carrier_tracking_url:
                    msg += "<a href=" + rec.carrier_tracking_url + " target='_blank'>" + rec.carrier_tracking_ref + "</a>."
                else:
                    msg += rec.carrier_tracking_ref + "."
                msg += "*"
            msg += "\n\nPlease find your delivery order attached for more details.\n\nThank you."

        # Account Invoice
        if active_model == 'account.move':
            msg = "Dear *PARTNER*"
            if rec.partner_id.parent_id:
                msg +="(" + rec.partner_id.parent_id.name +")"
            msg += "\n\nHere is your "
            if rec.name:
                msg += "invoice *" + rec.name + '*'
            else:
                'invoice'
            if rec.invoice_origin:
                msg += " (with reference: " + rec.invoice_origin + ")"
            msg += " amounting in *" + self.format_amount(rec.amount_total, rec.currency_id) + "*"
            msg += " from " + rec.company_id.name + "."
            if rec.state == 'paid':
                msg += " This invoice is already paid."
            else:
                msg += " Please remit payment at your earliest convenience."
            msg += "\nDo not hesitate to contact us if you have any question."

        # Account Payment
        if active_model == 'account.payment':
            msg = "Dear *PARTNER*\n\nThank you for your payment." \
            "Here is your payment receipt *" + (rec.name or '').replace('/','-') + "* amounting"\
            " to *" + self.format_amount(rec.amount, rec.currency_id) + "*"\
            " from " + rec.company_id.name + "."
            msg += "\nDo not hesitate to contact us if you have any question.\n\nBest regards."


        result['message'] = msg
        return result
