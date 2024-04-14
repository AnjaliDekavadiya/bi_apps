# -*- coding: utf-8 -*-

import base64
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

from odoo import http, _
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal as website_account

class LaundryBusinessService(http.Controller):

    @http.route(['/page/laundry_business_service_ticket'], type='http', auth="public", website=True)
    def laundry_business_service_request(self, **post):
        service_ids = request.env['laundry.service.type.custom'].sudo().search([])
        return request.render("laundry_iron_business.website_laundry_service_support_ticket", {
            'service_ids': service_ids,
        })

    def _prepare_laundry_business_service_vals(self, Partner, post):
        team_obj = request.env['laundry.business.team']
        team_match = team_obj.sudo().search([('is_team','=', True)], limit=1)
        services = request.httprequest.values.getlist('request_service_check')
        exp_date = post['expected_pickup_date']
        if exp_date:
            # date = datetime.strptime(str(exp_date), '%d/%m/%Y')
            date = datetime.strptime(str(exp_date), '%d/%m/%Y').date()
        if Partner:
            Partner = Partner.id
        else: 
            Partner = False
        return {
            'subject': post['subject'],
            'team_id': team_match.id,
            'user_id': team_match.leader_id.id,
            'team_leader_id': team_match.leader_id.id,
            'email': post['email'],
            'phone': post['phone'],
            'description': post['description'],
            'pickup_type': post['pickup_type'],
            'expected_pickup_date': date,
            'address': post['pickup_address'],
            'partner_id': Partner,
            'nature_of_service_id':[(6, 0, map(int, services))],
            'custome_client_user_id': request.env.user.id,
         }

    @http.route(['/laundry_iron_business/request_submitted'], type='http', auth="public", methods=['POST'], website=True)
    def request_submitted(self, **post):
        if request.env.user.has_group('base.group_public'):
            Partner = request.env['res.partner'].sudo().search([('email', '=', post['email'])], limit=1)
        elif request.env.user.partner_id:
            Partner = request.env.user.partner_id
        else:
            Partner = False 
        # if Partner:
        team_obj = request.env['laundry.business.team']
        team_match = team_obj.sudo().search([('is_team','=', True)], limit=1)
        laundry_service_vals = self._prepare_laundry_business_service_vals(Partner, post)
        support = request.env['laundry.business.service.custom'].sudo().create(laundry_service_vals)
        values = {
            'support':support,
            'user':request.env.user
        }
        # attachment_list = request.httprequest.files.getlist('attachment')
        # for image in attachment_list:
        #     if post.get('attachment'):
        #         attachments = {
        #                    'res_name': image.filename,
        #                    'res_model': 'laundry.business.service.custom',
        #                    'res_id': support,
        #                    'datas': base64.encodebytes(image.read()),
        #                    'type': 'binary',
        #                    'name': image.filename,
        #                }
        #         attachment_obj = http.request.env['ir.attachment']
        #         attach = attachment_obj.sudo().create(attachments)
        # if len(attachment_list) > 0:
        #     group_msg = _('Customer has sent %s attachments to this laundry business. Name of attachments are: ') % (len(attachment_list))
        #     for attach in attachment_list:
        #         group_msg = group_msg + '\n' + attach.filename
        #     group_msg = group_msg + '\n'  +  '. You can see top attachment menu to download attachments.'
        #     support.sudo().message_post(body=group_msg,message_type='comment')
        return request.render('laundry_iron_business.thanks_mail_send_laundry', values)
        # else:
        #     return request.render('laundry_iron_business.support_invalid_laundry',{'user':request.env.user})
                  
    @http.route(['/laundry_business_service_email/feedback/<int:order_id>'], type='http', auth='public', website=True)
    def feedback_email(self, order_id, **kw):
        values = {}
        values.update({'laundry_ticket_id': order_id})
        return request.render("laundry_iron_business.laundry_business_feedback", values) 
       
    @http.route(['/laundry_service/feedback/'],
                methods=['POST'], auth='public', website=True)
    def start_rating(self, **kw):
        partner_id = kw['partner_id']
        user_id = kw['laundry_ticket_id']
        laundry_obj = request.env['laundry.business.service.custom'].sudo().browse(int(user_id))
        #if partner_id == UserInput.partner_id.id:
        vals = {
              'rating':kw['star'],
              'comment':kw['comment'],
            }
        laundry_obj.sudo().write(vals)
        customer_msg = _(laundry_obj.partner_id.name + 'has send this feedback rating is %s and comment is %s') % (kw['star'],kw['comment'],)
        laundry_obj.sudo().message_post(body=customer_msg)
        #return http.request.render("machine_repair_management.successful_feedback")
        return http.request.render("laundry_iron_business.successful_feedback_laundry")
            
class website_account(website_account):

    def _prepare_portal_layout_values(self): # odoo11
        values = super(website_account, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'laundry_request_count': request.env['laundry.business.service.custom'].sudo().search_count([('partner_id', 'child_of', [partner.commercial_partner_id.id])]),
        })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        lead_object = request.env['crm.lead']
        values['laundry_request_count'] = request.env['laundry.business.service.custom'].sudo().search_count([('partner_id', 'child_of', [partner.commercial_partner_id.id])])
        return values
        
    @http.route(['/my/laundry_requests', '/my/laundry_requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_repair_request(self, page=1, **kw):
        response = super(website_account, self)
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        lr_obj = http.request.env['laundry.business.service.custom']
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id])
        ]
        # pager
        pager = request.website.pager(
            url="/my/laundry_requests",
            total=values.get('laundry_request_count'),
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        laundry_request = lr_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'laundry_requests': laundry_request,
            'page_name': 'laundry_requests',
            'pager': pager,
            'default_url': '/my/laundry_requests',
        })
        return request.render("laundry_iron_business.display_laundry_business_requests", values)
       
    @http.route(['/my/laundry_request/<model("laundry.business.service.custom"):laundry_request>'], type='http', auth="user", website=True)
    def my_laundry_request(self, laundry_request=None, **kw):
        # attachment_list = request.httprequest.files.getlist('attachment')
        # laundry_obj = http.request.env['laundry.business.service.custom'].sudo().browse(laundry_request.id)
        # for image in attachment_list:
        #     if kw.get('attachment'):
        #         attachments = {
        #                    'res_name': image.filename,
        #                    'res_model': 'laundry.business.service.custom',
        #                    'res_id': laundry_request.id,
        #                    'datas': base64.encodebytes(image.read()),
        #                    'type': 'binary',
        #                    'name': image.filename,
        #                }
        #         attachment_obj = http.request.env['ir.attachment']
        #         attachment_obj.sudo().create(attachments)
        # if len(attachment_list) > 0:
        #     group_msg = _('Customer has sent %s attachments to this Laundry Service Request. Name of attachments are: ') % (len(attachment_list))
        #     for attach in attachment_list:
        #         group_msg = group_msg + '\n' + attach.filename
        #     group_msg = group_msg + '\n'  +  '. You can see top attachment menu to download attachments.'
        #     laundry_obj.sudo().message_post(body=group_msg,message_type='comment')
        #     customer_msg = _('%s') % (kw.get('ticket_comment'))
        #     laundry_obj.sudo().message_post(body=customer_msg,message_type='comment')
        #     return http.request.render('laundry_iron_business.successful_laundry_ticket_send',{
        #     })
        # if kw.get('ticket_comment'):
        #     return http.request.render('laundry_iron_business.successful_laundry_ticket_send',{
        #     })
        return request.render("laundry_iron_business.display_laundry_service_request_from", {'laundry_request': laundry_request, 'user': request.env.user})
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
