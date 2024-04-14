# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError

class HelpdeskSupport(models.Model):

    _inherit = 'helpdesk.support'

    signature = fields.Binary(
        'Customer Signature', 
        help='Signature received through the portal.', 
        copy=False
    )
    
    signature_date = fields.Date(
        'Signature Date',
        readonly=True
    )
    
#    def _compute_access_url(self):
#        super(HelpdeskSupport, self)._compute_access_url()
#        for order in self:
#            if order.partner_id == self.env.user.partner_id:
#                if self.env.user.has_group('base.group_portal'):
#                    order.access_url = '/my/ticket/%s' % (order.id)
#            else:
#                order.access_url = '/technician/ticket/%s' % (order.id)


    #@api.multi
    def send_signature_request(self):
        if self.partner_id:
            template_id = self.env.ref('helpdesk_ticket_customer_signature.email_template_for_send_signature_request')
#        template_id.send_mail(self.id)
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069')
            url = "%s/my/ticket/%s" %(base_url, self.id)
            base_context = self.env.context.copy()

            template_id.sudo().with_context(link = url).send_mail(self.id)
        else:
            raise UserError(('Please set customer to send signature.'))

    def _get_ticket_customer_signature(self):#13
        self.ensure_one()
        return '/my/ticket/'+str(self.id)+'/accept'
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
