# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import werkzeug
import json
import base64
import odoo.http as http
from odoo import api, fields, models, tools, _
from odoo.http import request
from odoo import SUPERUSER_ID
from datetime import datetime, timedelta, time
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import odoo.http as http
from odoo.exceptions import UserError, ValidationError


class JobWorkorder(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'job_order_count' in counters:
            job_order_obj = request.env['job.order']
            job_order_count = job_order_obj.search_count([])
            
            values.update({
                'job_order_count': job_order_count,
            })
        return values

    def _prepare_portal_layout_values(self):
        values = super(JobWorkorder, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        job_order_obj = request.env['job.order']
        job_order_count = job_order_obj.search_count([])
        
        values.update({
            'job_order_count': job_order_count,
        })
        return values

    @http.route(['/your/job_order', '/your/job_order/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_job_order(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        job_order_obj = request.env['job.order']
        domain = []
        job_order_count = job_order_obj.search_count(domain)
        pager = portal_pager(
            url="/your/job_order",
            total=job_order_count,
            page=page,
            step=self._items_per_page
        )
        order = job_order_obj.search(domain, offset=pager['offset'])
        request.session['my_order_history'] = order.ids[:100]

        values.update({
            'order': order.sudo(),
            'page_name': 'order',
            'pager': pager,
            'default_url': '/your/job_order',
        })
        return request.render("bi_website_job_workorder.order_view_list", values)

    @http.route('/create/workorder', type="http", auth="public", website=True)
    def create_job_workorder(self, **post):
        name = ""
        if http.request.env.user.name != "Public user":
            name = http.request.env.user.name

            customer = http.request.env.user.partner_id.name
            email = http.request.env.user.partner_id.email
            phone = http.request.env.user.partner_id.phone
            values = {'name': customer, 'user_ids': name, 'email': email, 'phone': phone}

            return http.request.render('bi_website_job_workorder.create_job_workorder', values)
        else:
            return request.redirect('/web/login')

    @http.route('/create/workorder/thanks', type="http", auth="public", website=True)
    def job_order_thanks(self, **post):
        if post.get('debug') or not post:
            return request.render("bi_website_job_workorder.workorder_thank_you")
        partner_brw = request.env['res.users'].sudo().browse(request.env.user.id)
        Attachments = request.env['ir.attachment']
        upload_file = post['upload']
        subject = post['subject']
        name = post['name']
        email = post['email']
        phone = post['phone']
        project = post['website_project']
        priority = post['priority']
        description = post['description']

        vals = {
            'name': subject,
            'priority': priority,
            'start_date': datetime.now(),
            'customer_id': partner_brw.partner_id.id,
            'customer_name': name,
            'customer_email': email,
            'customer_phone': phone,
            'description': description,
            'project_id': project
        }

        job_order_obj = request.env['job.order'].sudo().create(vals)
        if upload_file:
            attachment_id = Attachments.sudo().create({
                'name': upload_file.filename,
                'type': 'binary',
                'datas': base64.encodebytes(upload_file.read()),
                'public': True,
                'res_model': 'ir.ui.view',
                'job_order_id': job_order_obj.id,
            })

        user = request.env['res.users'].sudo().browse(request.env.user.id)
        user_from = request.env['res.users'].sudo().search([('company_id', '=', request.env.user.company_id.id)],
                                                           limit=1)
        template_id = request.env['ir.model.data']._xmlid_lookup('bi_website_job_workorder.email_template_job_order')
        email_template_obj = request.env['mail.template'].sudo().browse(template_id[1])
        if template_id:
            values = email_template_obj._generate_template(job_order_obj.ids,
                                                       ['subject', 'body_html', 'email_from', 'email_to', 'partner_to',
                                                        'email_cc', 'reply_to', 'scheduled_date'])
            for res_id, values in values.items():
                values['email_from'] = user_from.partner_id.email
                values['email_to'] = user.partner_id.email
                values['author_id'] = user.partner_id.id
                values['res_id'] = False
                mail_mail_obj = request.env['mail.mail']
                msg_id = mail_mail_obj.sudo().create(values)
                if msg_id:
                    mail_mail_obj.send([msg_id])
        return request.render("bi_website_job_workorder.workorder_thank_you")

    @http.route('/order/view', type="http", auth="user", website=True)
    def order_view_list(self, **kw):
        return http.request.render('bi_website_job_workorder.order_view_list')

    @http.route(['/order/view/detail/<model("job.order"):order>'], type='http', auth="public", website=True)
    def job_order_view(self, order, category='', search='', **kwargs):

        context = dict(request.env.context or {})
        job_order_obj = request.env['job.order']
        context.update(active_id=order.id)
        job_order_data_list = []
        job_order_data = job_order_obj.browse(int(order))

        for items in job_order_data:
            job_order_data_list.append(items)

        return http.request.render('bi_website_job_workorder.job_order_view', {
            'job_order_data_list': order
        })

    def _order_check_access(self, job_order_id, access_token=None):
        order = request.env['job.order'].browse([job_order_id])
        order_sudo = order.sudo()
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(order_sudo.access_token, access_token):
                raise
        return order_sudo

    @http.route(['/my/job/orders/pdf/<int:job_order_id>'], type='http', auth="public", website=True)
    def portal_job_order_report(self, job_order_id, access_token=None, **kw):
        try:
            order_sudo = self._order_check_access(job_order_id, access_token)
        except AccessError:
            return request.redirect('/my')

        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('bi_website_job_workorder.website_job_order_report_id', [order_sudo.id])
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

        pdf = request.env.ref('bi_website_job_workorder.website_job_order_report_id').sudo()._render_qweb_pdf([order_sudo.id],data={'report_type': 'pdf'})[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
