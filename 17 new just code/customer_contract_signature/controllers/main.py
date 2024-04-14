# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression
import datetime

class ContractCustomerSignature(CustomerPortal):

#    @http.route(['/my/contract/accept'], type='json', auth="public", website=True)
    @http.route(['/my/contract/<int:res_id>/accept'], type='json', auth="public", website=True)
    def contract_quote_accept_signature(self, res_id, access_token=None, partner_name=None, signature=None, order_id=None):
        contract_sudo = request.env['account.analytic.account'].sudo().browse(res_id)
#        try:
#            contract_sudo = self._document_check_access('account.analytic.account', res_id, access_token=access_token)
#        except (AccessError, MissingError):
#            return {'error': _('Invalid Contract')}
        if not signature:
            return {'error': _('Signature is missing.')}
        else:
            contract_sudo.custom_signature_date = datetime.date.today()
        contract_sudo.custom_signature = signature
#        contract_sudo.partner_id.name = partner_name
        if contract_sudo.custom_signature:
            recipient_ids_vals=[]
            template_id = request.env.ref('customer_contract_signature.email_template_for_contract_signature')
            for partner_ids in contract_sudo.message_partner_ids:
                value = (4,partner_ids.id)
                recipient_ids_vals.append(value)
            partner_id_vals = (4,contract_sudo.partner_id.id)
            recipient_ids_vals.append(partner_id_vals)
            email_values={'recipient_ids':recipient_ids_vals}
            template_id.sudo().send_mail(res_id,email_values=email_values)
        return {
            'force_refresh': True,
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
