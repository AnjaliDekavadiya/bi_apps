# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class website_sale(WebsiteSale):

    def create_request_demo(self, user, product, name, email, description):
        medium = request.env['utm.medium'].search([('name','=','Website')], limit=1)
        if product.default_code:
            product = 'request demo for '+' ['+product.default_code+'] '+product.name
        else:
            product = 'request demo for '+product.name
        values = {
                'name': product,
                'contact_name':name,
                'email_from': email,
                'description': description,
                'medium_id': medium and medium.id or False,
                }
        crm_lead = request.env['crm.lead'].sudo().create(values)
        return crm_lead
        
    @http.route(['/request/demo'], type='http', auth="public", methods=['GET'], website=True)
    def request_product_email(self, **kw):
        """ Notify Product Email"""
        values = {}
        local_context = http.request.env.context.copy()
        
        for field_name, field_value in kw.items():
            values[field_name] = field_value
        user = http.request.env.user
        if user.has_group('base.group_public'):
            name = values['name']
            email = values['email']
        else:
            name = user.name
            email = user.email
        description = values['description']
        product = request.env['product.template'].browse(int(values['product_id']))
        lead = self.create_request_demo(user, product, name, email, description)#Create lead
        demo_template = request.env.ref('website_product_demo.email_template_physical_demo')
        demo_template.sudo().send_mail(lead.id, force_send=True)
        return http.request.render('website_product_demo.thanks_notification_received',{})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
