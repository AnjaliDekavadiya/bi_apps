# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError

class AnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    custom_signature = fields.Binary(
        'Customer Signature', 
        help='Signature received through the portal.', 
        copy=False
    )
    
    custom_signature_date = fields.Date(
        'Signature Date',
        readonly=True
    )
    
#    @api.multi
    def send_signature_contract_request(self):
        self.ensure_one()
        if self.partner_id:
            template_id = self.env.ref('customer_contract_signature.email_template_for_contract_signature_request')
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069')
            # url = "%s/my/contract/%s" %(base_url, self.id)
            url = "%s/my/custom/contract/%s" %(base_url, self.id) #odoo13
            base_context = self.env.context.copy()
            template_id.sudo().with_context(base_context,
                link = url,
            ).send_mail(self.id)
        else:
            raise UserError(('Please set customer to send signature.'))

    def _get_signature_url(self):
        self.ensure_one()
        return '/my/contract/'+str(self.id)+'/accept'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
