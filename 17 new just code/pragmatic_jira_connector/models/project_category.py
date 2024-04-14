# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class JiraProjectCategory(models.Model):
    _name = 'jira.category'
    _description = 'Jira Project Category'

    def receive_all(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            for pc in company_id.get('projectCategory').json():
                self.process_response(pc)

    def process_response(self, response):
        category_dict = dict(
            jira_id=response['id'],
            description=False,
            name=response['name']
        )
        if 'description' in response:
            category_dict['description'] = response['description']
        category = self.search([('jira_id', '=', category_dict['jira_id'])])
        if not category:
            category = self.create(category_dict)
        else:
            category.write(category_dict)
        return category

    def key_operation(self, id):
        category = self.search([('jira_id', '=', id)])
        if not category:
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                category = self.process_response(company_id.get('projectCategory/' + str(id)).json())
        return category

    name = fields.Char(required=1)
    jira_id = fields.Char(required=1)
    description = fields.Char()
