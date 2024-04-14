# -*- coding: utf-8 -*-

from odoo import fields, models
from dateutil import parser
import base64


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    # Unlink attachment from odoo .

    def unlink(self):
        for j_id in self:
            jira_id = j_id.jira_id
            if jira_id:
                company_id = None
                user_id = self.env['res.users'].search([])
                for c_id in user_id.company_ids:
                    if c_id.account_id:
                        company_id = c_id
                if company_id:
                    company_id.delete('attachment/' + jira_id)
        return super(Attachment, self).unlink()

    def while_import_attachemnt(self, issue, response):
        if not self.search([('jira_id', '=', response['id'])]):
            created_date = parser.parse(response['created']).strftime("%Y-%m-%d %H:%M:%S")
            created_date = parser.parse(created_date)
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                resp = company_id.get_file(response['content']).content
                self.create(dict(datas=base64.b64encode(resp),
                                 name=response['filename'],
                                 res_model='project.task',
                                 res_id=issue.id,
                                 jira_id=response['id'],
                                 issue_id=issue.id,
                                 author_id=self.env['res.users'].get_user_by_dict(response['author']).id,
                                 ))

    jira_id = fields.Char(string='Jira ID')
    issue_id = fields.Many2one('project.task')
    author_id = fields.Many2one('res.users')
