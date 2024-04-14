# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request

class CustomWebsiteAskQuestion(http.Controller):

    @http.route(['/custom/ask/question'], type='json', auth="public", website=True)
    def custom_probc_ask_question(self, **post):
        values={
            'name':post['disc'],
            'contact_name': post['name'],
            'email_from':post['email'],
            'phone': post['phone'],
            'description': post['detail'],
            'type': 'lead'
        }
        if request.env.user:
            values.update({
                'partner_id': request.env.user.partner_id.id
                })
        crm_lead = request.env['crm.lead'].sudo().create(values)
