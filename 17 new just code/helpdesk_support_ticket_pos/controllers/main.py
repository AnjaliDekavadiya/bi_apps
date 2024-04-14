# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request

class HelpdeskPOSSupport(http.Controller):
    
    @http.route(['/helpdesk_pos_support_ticket/<int:pos_order_id>'], type='http', auth="public", website=True)
    def pos_ticket_submitted_custom(self, pos_order_id=None, **post):
        values = {'pos_order_id': request.env['pos.order'].browse(int(pos_order_id))}
        return request.render('website_helpdesk_support_ticket.website_helpdesk_support_ticket', values)

    @http.route(['/custom/helpdesk_pos'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def custom_helpdesk_pos_json(self):
        pos_ids = http.request.env['pos.order'].search([('partner_id', 'child_of', request.env.user.partner_id.commercial_partner_id.id)])
        # return {
        #     'html': request.env.ref('helpdesk_support_ticket_pos.custom_customer_pos_order')._render({
        #         'pos_ids': pos_ids,
        #     })
        # }
        return {
            'html': request.env['ir.qweb']._render('helpdesk_support_ticket_pos.custom_customer_pos_order', {
                'pos_ids': pos_ids,
            })
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: