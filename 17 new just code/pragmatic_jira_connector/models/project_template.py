# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class JiraProjectTemplate(models.Model):
    _name = 'jira.project.template'
    _description = 'Jira Project Template'

    def receive_all(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            response = company_id.get('templates', '/rest/project-templates/1.0/').json()
            for type in response['projectTemplatesGroupedByType']:
                for pt in type['projectTemplates']:
                    self.process_response(pt)

    def process_response(self, response):
        project_template_dict = dict(
            name=response['name'],
            create_project=response['createProject'],
            description=response['description'],
            long_description=response['longDescriptionContent'],
            project_type_id=self.env['jira.type'].key_operation(response['projectTypeKey']).id,
            weight=response['weight'],
            key=response['itemModuleCompleteKey'],
        )
        project_template = self.search([('key', '=', response['itemModuleCompleteKey'])])
        if not project_template:
            project_template = self.create(project_template_dict)
        else:
            project_template.write(project_template_dict)
        return project_template

    def key_operation(self, key):
        pass

    name = fields.Char()
    key = fields.Char()
    create_project = fields.Boolean()
    description = fields.Char()
    long_description = fields.Char()
    project_type_id = fields.Many2one('jira.type')
    weight = fields.Integer()
