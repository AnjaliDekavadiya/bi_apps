# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import base64
from odoo.http import request
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta, time
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import odoo.http as http


class RFIInformation(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'rfi_count' in counters:
            request_information_obj = request.env['request.information']
            rfi_count = request_information_obj.search_count([])

            values.update({
                'rfi_count': rfi_count,
            })
        return values

    def _prepare_portal_layout_values(self):
        values = super(RFIInformation, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        request_information = request.env['request.information']
        rfi_count = request_information.search_count([('partner_id','=',partner.id)])

        values.update({
            'rfi_count': rfi_count,
        })
        return values

    @http.route(['/my/rfis', '/my/rfis/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_rfi(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        request_information = request.env['request.information']
        domain = []
        rfi_count = request_information.search_count(domain)
        pager = portal_pager(
            url="/my/rfis",
            total=rfi_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        partner = request.env.user.partner_id
        rfis = request_information.sudo().search([('partner_id', '=', partner.id)], offset=pager['offset'])
        request.session['my_rfi_history'] = rfis.ids[:100]

        values.update({
            'rfis': rfis,
            'page_name': 'RFI',
            'pager': pager,
            'default_url': '/my/rfis',
        })
        return request.render("bi_website_project_request_for_information.portal_my_rfi", values)

    @http.route('/create/information', type="http", auth="public", website=True)
    def CreateRFIInfo(self, **kw):
        name = ""
        if http.request.env.user.name != "Public user":
            name = http.request.env.user.name

        customer = http.request.env.user.partner_id.name
        email = http.request.env.user.partner_id.email
        phone = http.request.env.user.partner_id.phone
        values = {'name': customer, 'user_ids': name, 'email': email, 'phone': phone}

        return http.request.render('bi_website_project_request_for_information.create_rfi_information', values)

    @http.route('/rfi/info/thanks', type="http", auth="public", website=True)
    def RFIInfoThanks(self, **post):
        if not post:
            return request.render("bi_website_project_request_for_information.rfi_info_thank_you")

        partner_brw = request.env['res.users'].sudo().browse(request.env.user.id)
        Attachments = request.env['ir.attachment']
        upload_file = ''
        if 'upload' in post:
            upload_file = post.get('upload')

        name = post.get('subject')
        assign_to_id = post.get('name')
        email = post.get('email')
        phone = post.get('phone')
        category = post.get('rfi_category_id')
        description = post.get('description')
        priority = post.get('priority')
        vals = {
            'name': name,
            'description': description,
            'email': email,
            'phone': phone,
            'rfi_category_id': category,
            'priority': priority,
            'partner_id': partner_brw.partner_id.id,
            'company_id': partner_brw.company_id.id,
            'create_date': datetime.now(),
        }

        vals = {
            'name': name,
            'description': description,
            'email': email,
            'phone': phone,
            'rfi_category_id': category,
            'priority': priority,
            'partner_id': partner_brw.partner_id.id,
            'company_id': partner_brw.company_id.id,
            'create_date': datetime.now(),
        }

        request_information_obj = request.env['request.information'].sudo().create(vals)
        if upload_file:
            attachment_id = Attachments.sudo().create({
                'name': upload_file.filename,
                'type': 'binary',
                'datas': base64.encodebytes(upload_file.read()),
                'public': True,
                'res_model': 'ir.ui.view',
                'rfi_info_id': request_information_obj.id,
            })

        user = request.env['res.users'].sudo().browse(SUPERUSER_ID)
        template_id = request.env['ir.model.data']._xmlid_lookup(
            'bi_website_project_request_for_information.email_template_rfi_information')[1]
        email_template_obj = request.env['mail.template'].sudo().browse(template_id)
        if template_id:
            values = email_template_obj._generate_template(request_information_obj.ids,
                                                       ['body_html', 'email_from', 'email_to', 'partner_to',
                                                               'email_cc', 'reply_to', 'scheduled_date'])
            for res_id, values in values.items():
                values['email_from'] = user.email
                values['email_to'] = email
                values['res_id'] = False
                values['subject'] = name
                mail_mail_obj = request.env['mail.mail']
                msg_id = mail_mail_obj.sudo().create(values)
                if upload_file:
                    msg_id.attachment_ids = [(6, 0, [attachment_id.id])]
                if msg_id:
                    mail_mail_obj.send([msg_id])

        return request.render("bi_website_project_request_for_information.rfi_info_thank_you")

    @http.route(['/my/rfi/<int:rfi>'], type='http', auth="user", website=True)
    def rfi_view(self, rfi=None, **kw):
        rfi_id = request.env['request.information'].browse(rfi)
        return request.render("bi_website_project_request_for_information.rfi_view", {'rfi': rfi_id})

    @http.route(['/rfi/message'], type='http', auth="public", website=True)
    def rfi_message(self, **post):

        upload_file = ''
        Attachments = request.env['ir.attachment']
        if 'upload' in post:
            upload_file = post.get('upload')
        if post.get('rfi_id'):
            if ',' in post.get('rfi_id'):
                bcd = post.get('rfi_id').split(',')
            else:
                bcd = [post.get('rfi_id')]

            request_information_obj = request.env['request.information'].sudo().search([('id', '=', bcd)])

            if upload_file:
                attachment_id = Attachments.sudo().create({
                    'name': upload_file.filename,
                    'type': 'binary',
                    'datas': base64.encodebytes(upload_file.read()),
                    'public': True,
                    'res_model': 'request.information',
                    'res_id': request_information_obj.id,
                    'rfi_info_id': request_information_obj.id,
                })

        context = dict(request.env.context or {})
        request_information = request.env['request.information']
        if post.get('message'):
            message_id1 = request_information_obj.message_post()

            message_id1.body = post.get('message')
            message_id1.message_type = 'comment'
            message_id1.model = 'request.information'
            message_id1.res_id = post.get('rfi_id')

        return http.request.render('bi_website_project_request_for_information.rfi_message_thank_you')

    @http.route(['/rfi/comment/<model("request.information"):rfi>'], type='http', auth="public", website=True)
    def rfi_comment_page(self, rfi, **post):

        return http.request.render('bi_website_project_request_for_information.rfi_comment', {'rfi': rfi})

    @http.route(['/rfi/comment/send'], type='http', auth="public", website=True)
    def rfi_comment(self, **post):

        context = dict(request.env.context or {})
        if post.get('rfi_id'):
            request_information_obj = request.env['request.information'].browse(int(post.get('rfi_id')))
            request_information_obj.update({
                'customer_rating': post.get('customer_rating'),
                'comment': post.get('comment'),
            })
        return http.request.render('bi_website_project_request_for_information.rfi_rating_thank_you')

