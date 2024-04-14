# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class website(models.Model):
    _inherit = 'website'

    task_id = fields.Many2one('project.task')
    project_id = fields.Many2one('project.project')

    def get_project_details_for_note(self):
        project_ids = self.env['project.project'].sudo().search([])
        partner = self.env['res.partner'].browse(self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id)
        projects = []
        for i in project_ids :
            if partner in i.message_partner_ids :
                projects.append(i)
        return projects

    def get_task_details_for_note(self):

        projects = self.get_project_details_for_note()
        partner = self.env['res.partner'].browse(self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id)
        tasks = []

        for p in projects:
            for t in p.task_ids:
                tasks.append(t)
        return tasks

    def get_task_tag_ids(self):
        tag_ids = self.env['project.tags'].sudo().search([])

        tag = []
        for p in tag_ids:
            tag.append(p)
        return tag
