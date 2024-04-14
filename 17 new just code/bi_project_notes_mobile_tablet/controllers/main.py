# # -*- coding: utf-8 -*-
# # Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
#
from odoo import SUPERUSER_ID, http, tools, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
class bi_website_note(CustomerPortal):

    @http.route(['/my/add_new_note'], type='http', auth="public", website=True)
    def add_new_note(self,forum=None,page=1, **kwargs):

        partner = request.env.user.partner_id
        return request.render("bi_project_notes_mobile_tablet.bi_new_note_form")

    @http.route(['/my/new_note_submit'], type='http',methods=['POST'], auth="public", website=True)
    def submit_new_note(self, **post):
        ids = request.httprequest.form.getlist('tasks')
        tag_ids = []
        for rec in ids:
            tmp = list(rec)
            tag_ids.append(tmp[1])
        if post.get('debug'):
            return request.render("bi_project_notes_mobile_tablet.note_added")
        if post:
            partner = request.env.user.id
            partner_id = request.env['res.users'].sudo().search([('id', '=', partner)])
            task_obj = request.env['project.task']
            task_id = task_obj.create({
                'name':post['post_name'],
                'tag_ids':[(6,0,tag_ids)],
                'description':post['content'],
            })

            return request.render("bi_project_notes_mobile_tablet.note_added")

    @http.route(['/edit_note/<model("project.task"):note>'], type='http', auth="public", website=True)
    def edit_note(self, note, category='', search='', **kwargs):
        return request.render("bi_project_notes_mobile_tablet.bi_portal_edit_note", {'note': note})

    @http.route(['/delete_note/<model("project.task"):note>'], type='http', auth="public", website=True)
    def delete_note(self, note, category='', search='', **kwargs):
        request.env["project.task"].search([('id', '=', note.id)]).unlink()
        return request.redirect("/my/home")
#
    @http.route(['/my/save_edit_note'], type='http', auth="public", website=True)
    def edit_note_save(self, context=None, **post):
        val = (request.httprequest.__dict__)
        array = val.get('environ').get('HTTP_REFERER').split('/')
        array2 = val.get('environ').get('HTTP_REFERER').split('/')[len(array) - 1].split('-')
        property_url_id = array2[len(array2) - 1]
        if post.get('debug'):
            return request.render("bi_project_notes_mobile_tablet.note_updated")

        partner = request.env.user.id
        partner_id = request.env['res.users'].sudo().search([('id', '=', partner)])
        task_obj = request.env['project.task'].sudo().search([('id', '=', property_url_id)])
        if task_obj and post:
            task_obj.update({
                'name': post['post_name'],
                'description': post['content'],
            })

        return request.render("bi_project_notes_mobile_tablet.note_updated")
