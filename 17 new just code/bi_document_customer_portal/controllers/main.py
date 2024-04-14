# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import werkzeug
import json
import base64
import io

import odoo.http as http
from odoo.http import request
from odoo import SUPERUSER_ID, _
from datetime import datetime, timedelta, time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import odoo.http as http


class WebsiteDocumentOrder(CustomerPortal):


    @http.route(['/my/my_document', '/my/my_document/page/<int:page>'], type='http', auth="user", website=True)
    def portal_document_list(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        my_document = request.env['directorie.document']
        domain = []

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name desc'},
        }

        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        repair_count = my_document.search_count(domain)
        
        
        pager = portal_pager(
            url="/my/my_document",
            total=repair_count,
            page=page,
            step=self._items_per_page
        )
        
        document = my_document.search([])
        partner = request.env.user.partner_id
        
        values.update({
            'document': document,
            'page_name': 'my_document',
            'pager': pager,
            'default_url': '/my/my_document',
        })
        
        return request.render("bi_document_customer_portal.portal_document_list", values)


    @http.route(['/document/view/detail/<model("directorie.document"):attachment>'],type='http',auth="public",website=True)
    def portal_attachment_view(self, attachment, category='', search='', **kwargs):
        proj_onj = request.env['ir.attachment'].sudo().search([])
        if attachment.model:
            attachment_obj = request.env['ir.attachment'].sudo().search([('res_model','=',attachment.model.model),("directory_id",'=',attachment.id)])
        if not attachment.model:
            attachment_obj = request.env['ir.attachment'].sudo().search([("directory_id",'=',attachment.id)])
        current = request.env.uid
        user_in = request.env['res.users'].sudo().browse([current])
        list_attach = []
        object_list = []
        for objects in attachment_obj:
            for user_por in objects.user_ids:
                if user_por.name == user_in.name:
                    object_list.append(objects)
        return http.request.render('bi_document_customer_portal.portal_attachment_view',{
            'list_attach':object_list,
            'attachment':attachment
            })

    @http.route(['/my/document/<int:attachment>'], type='http', auth="public", website=True)
    def attachment_view_form(self,attachment, **post):
        attachment = request.env['ir.attachment'].sudo().search([('id','=',attachment)])
        return request.render("bi_document_customer_portal.attachment_view_form",{'attachment':attachment})

    @http.route(['/attachment/download'], type='http', auth='public')
    def download_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas","res_model", "res_id", "type", "url"]
        )

        if attachment:
            attachment = attachment[0]
        else:
            return redirect('/shop')

        if attachment["type"] == "url":
            if attachment["url"]:
                return redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = base64.standard_b64decode(attachment["datas"])
            image_data = io.BytesIO(data)
            return http.send_file(image_data, filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()


    @http.route(['/my/document/search'], type='http', auth="public", website=True)
    def search_timesheet_box(self,**post):

        search_string = str(post['document_search'])
        res = False
        if search_string:
            for search in search_string.split(" "):
                res = request.env['directorie.document'].sudo().search([('name', 'ilike', search)])

        return request.render("bi_document_customer_portal.search_document",{'document': res})

    @http.route(['/my/attachments/search'], type='http', auth="public", website=True)
    def search_times_box(self,**post):
        if post.get('attachment_search'):
            search_string = str(post['attachment_search'])
            res = False
            if search_string:
                attachment = request.env['directorie.document'].sudo().search([])
                for i in attachment:
                    list_at = []
                    attachment_objects = request.env['ir.attachment'].sudo().search([('res_model', '=', i.model.model)])    
                    for a in attachment_objects:
                        if search_string in a.name:
                            res = a
                            list_at.append(res)
                            

            return request.render("bi_document_customer_portal.search_attachments",{"attachment": res,
                                                                                    "list_attach":list_at})