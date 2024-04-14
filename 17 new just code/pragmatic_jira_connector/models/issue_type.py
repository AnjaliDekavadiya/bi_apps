# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class IssueType(models.Model):
    _name = 'issue.type'
    _description = 'Jira Issue Type'

    def receive_all(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            types = company_id.get('issuetype').json()
            for t in types:
                self.process_response(t)

    def process_response(self, response):
        type_dict = dict(
            jira_id=response['id'],
            description=response['description'],
            name=response['name'],
            subtask=response['subtask'],
        )
        t = self.search([('jira_id', '=', response['id'])])
        if not t:
            t = self.create(type_dict)
        else:
            t.write(type_dict)
        return t

    def key_operation(self, id):
        t = self.search([('jira_id', '=', id)])
        if not t:
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                t = self.process_response(company_id.get('issuetype/' + id).json())
        return t

    def jira_dict(self, it_dict):
        it = self.search([('jira_id', '=', it_dict['id'])])
        if not it:
            it = self.process_response(it_dict)
        return it

    jira_id = fields.Char()
    description = fields.Char()
    name = fields.Char()
    subtask = fields.Boolean()
