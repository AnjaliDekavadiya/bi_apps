# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression
import datetime

class HelpdeskTicketCustomerSignature(CustomerPortal):

#    @http.route(['/my/ticket/accept', '/my/ticket/<int:res_id>/accept'], type='json', auth="public", website=True)
    @http.route(['/my/ticket/accept', '/my/ticket/<int:res_id>/accept'], type='json', auth="public", website=True)
    def ticket_quote_accept_signature(self, res_id=None, access_token=None, partner_name=None, signature=None, order_id=None):
        try:
            order_sudo = self._document_check_access('helpdesk.support',res_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid ticket')}
        if not signature:
            return {'error': _('Signature is missing.')}
        else:
            order_sudo.signature_date = datetime.date.today()
        order_sudo.signature = signature
#        order_sudo.partner_id.name = partner_name
        if order_sudo.signature:
            recipient_ids_vals=[]
            template_id = request.env.ref('helpdesk_ticket_customer_signature.email_template_for_helpdesk_support_signature_mail')
            for partner_ids in order_sudo.message_partner_ids:
                value = (4,partner_ids.id)
                recipient_ids_vals.append(value)
            partner_id_vals = (4,order_sudo.partner_id.id)
            recipient_ids_vals.append(partner_id_vals)
            email_values={'recipient_ids':recipient_ids_vals}
            template_id.sudo().send_mail(res_id,email_values=email_values)
        return {
            'force_refresh': True,
        }

#    @http.route(['/technician/ticket/accept'], type='json', auth="public", website=True)
#    def ticket_quote_accept_signature_technician(self, res_id, access_token=None, partner_name=None, signature=None, order_id=None):
#        try:
#            order_sudo = self._document_check_access('helpdesk.support', res_id, access_token=access_token)
#        except (AccessError, MissingError):
#            return {'error': _('Invalid ticket')}
#        if not signature:
#            return {'error': _('Signature is missing.')}
#        else:
#            order_sudo.signature_date = datetime.date.today()
#        order_sudo.signature = signature
#        order_sudo.partner_id.name = partner_name
#        if order_sudo.signature:
#            recipient_ids_vals=[]
#            template_id = request.env.ref('helpdesk_ticket_customer_signature.email_template_for_helpdesk_support_signature_mail')
#            for partner_ids in order_sudo.message_partner_ids:
#                value = (4,partner_ids.id)
#                recipient_ids_vals.append(value)
#            partner_id_vals = (4,order_sudo.partner_id.id)
#            recipient_ids_vals.append(partner_id_vals)
#            email_values={'recipient_ids':recipient_ids_vals}
#            template_id.sudo().send_mail(res_id,email_values=email_values)
#        return {
#            'force_refresh': True,
#        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
