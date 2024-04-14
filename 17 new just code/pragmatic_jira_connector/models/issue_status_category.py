# -*- coding: utf-8 -*-

from odoo import fields, models


class StatusCategory(models.Model):
    _name = 'issue.status.category'
    _description = 'Jira Issue Status Category'

    def receive_all(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            scategory = company_id.get('statuscategory').json()
            for sc in scategory:
                self.process_response(sc)

    def process_response(self, response):
        sc_dict = dict(
            jira_id=response['id'],
            key=response['key'],
            name=response['name'],
        )
        sc = self.search([('key', '=', sc_dict['key'])])
        if not sc:
            sc = self.create(sc_dict)
        else:
            sc.write(sc_dict)
        return sc

    def key_operation(self, key):
        sc = self.search([('key', '=', key)])
        if not sc:
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                sc = self.process_response(company_id.get('statuscategory/' + key).json())
        return sc

    jira_id = fields.Char(required=1)
    key = fields.Char(required=1)
    name = fields.Char(required=1)
