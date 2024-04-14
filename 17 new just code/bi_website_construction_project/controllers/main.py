# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import werkzeug
from odoo import http
from odoo.http import request,Stream
import base64
import io


class ProjectConstruction(http.Controller):

    @http.route(['/projects'], type='http', auth="public", website=True)
    def projects(self, **post):
        project_category_ids = request.env['project.category'].search([])
        values = {'category_id': project_category_ids}
        return request.render("bi_website_construction_project.bi_project_construction", values)

    @http.route(['/project/category/view/<model("project.category"):project_category>'], type='http', auth="public",
                website=True)
    def project_category_view(self, project_category, category='', search='', **post):

        context = dict(request.env.context or {})
        project_obj = request.env['project.project']
        context.update(active_id=project_category.id)
        project_data_list = []
        project_data = project_obj.sudo().search([('category_id', '=', project_category.id)])
        project_category = request.env['project.category'].search([])

        for items in project_data:
            project_data_list.append(items)

        return http.request.render('bi_website_construction_project.project_view', {
            'project_data_list': project_data_list, 'categories': project_category
        })

    @http.route(['/project/view/<model("project.project"):project>'], type='http', auth="public", website=True)
    def project_details_view(self, project, category='', search='', **post):

        context = dict(request.env.context or {})
        project_obj = request.env['project.project']
        context.update(active_id=project.id)
        project_data = project_obj.sudo().browse(int(project))
        attachment = project_data.brochure_ids
        values = {'project': project_data, 'attachments': attachment}
        return http.request.render('bi_website_construction_project.project_details_view', values)

    @http.route(['/attachment/download'], type='http', auth='public')
    def download_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "type", "res_model", "res_id", "type", "url"]
        )

        if attachment:
            attachment = attachment[0]
        else:
            return werkzeug.utils.redirect('/shop')

        if attachment["type"] == "url":
            if attachment["url"]:
                return werkzeug.utils.redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = base64.standard_b64decode(attachment["datas"])
            image_data = io.BytesIO(data)
            return http.Stream.from_binary_field(attachment_id,image_data).get_response(filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()
