# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions


class JiraProject(models.Model):
    _inherit = 'project.project'

    def create_jira_dict(self):
        # print("\n\ncreate_jira_dict===============",vals,vals['user_id'])
        project_dict = dict()
        if self.name:
            project_dict['name'] = self.name
        if self.key:
            project_dict['key'] = self.key
        if self.project_type_id:
            project_dict['projectTypeKey'] = self.env['jira.type'].browse(self.project_type_id.id).key
        if self.user_id:
            project_dict['leadAccountId'] = self.env['res.users'].browse(self.user_id.id).jira_accountId
        if self.project_template_id:
            project_dict['projectTemplateKey'] = self.env['jira.project.template'].browse(
                self.project_template_id.id).key
        if self.description:
            if self.description:
                project_dict['description'] = self.description
            else:
                project_dict['description'] = ''
        if self.url:
            if self.url:
                project_dict['url'] = self.url
            else:
                project_dict['url'] = ''
        if self.category_id:
            if self.category_id:
                project_dict['categoryId'] = self.env['jira.category'].browse(self.category_id.id).jira_id
            else:
                project_dict['categoryId'] = ''

        return project_dict

    def export_project(self):
        # print("\n\n\nexport_project=============",self)
        response = False
        if 'disable_mail_mail' not in self.env.context and 'jira_project' in self and self.jira_project:
            project_dict = self.create_jira_dict()
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                # print("\n\n\n\n\nproject_dict===============", project_dict)
                response = company_id.post('project', project_dict)
                self.jira_id = response.json()['id']

        if response:
            self = self.with_context(dict(disable_mail_mail=True))
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                self.process_response(company_id.get('project/' + self.jira_id).json())

    # @api.model
    # def create(self, vals):
    #
    #     response = False
    #     if 'disable_mail_mail' not in self.env.context and 'jira_project' in vals and vals['jira_project']:
    #         project_dict = self.create_jira_dict(vals)
    #
    #         #print("\n\n\n\n\nproject_dict===============",project_dict)
    #         response = self.env['res.company'].search([],limit=1).post('project', project_dict)
    #         vals['jira_id'] = response.json()['id']
    #
    #     project = super(JiraProject, self).create(vals)
    #     if response:
    #         self = self.with_context(dict(disable_mail_mail=True))
    #         self.process_response(self.env['res.company'].search([],limit=1).get('project/' + project.jira_id).json())
    #     return project

    def write(self, vals):
        return super(JiraProject, self).write(vals)

    @api.onchange('jira_project')
    def onchange_context(self):
        if self.jira_project:
            if self.user_id and not self.user_id.jira_accountId:
                self.user_id = False
            return {'domain': {'user_id': [('jira_accountId', '!=', False)]}}
        else:
            return {'domain': {'user_id': []}}

    def receive_all(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            response = company_id.get('project').json()
            for p in response:
                self.process_response(company_id.get('project/' + p['key']).json())

    def process_response(self, response):
        # print("\n\n============",response['lead'])
        project_dict = dict(
            jira_id=response['id'],
            key=response['key'],
            description=False,
            user_id=self.env['res.users'].get_user_by_dict(response['lead']).id,
            name=response['name'],
            project_type_id=self.env['jira.type'].key_operation(response['projectTypeKey']).id,
            category_id=False,
            url=False,
            type_ids=[(6, 0, [])],
        )

        if 'projectCategory' in response:
            project_dict['category_id'] = self.env['jira.category'].key_operation(response['projectCategory']['id']).id
        if 'url' in response:
            project_dict['url'] = response['url']
        if response['description']:
            project_dict['description'] = response['description']

        issue_type_ids = list()
        for issue_type in response['issueTypes']:
            issue_type_ids.append(self.env['issue.type'].jira_dict(issue_type).id)
        project_dict['issue_type_ids'] = [(6, 0, issue_type_ids)]
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            types = company_id.get('project/' + response['key'] + '/statuses').json()[0]['statuses']
        type_ids = []
        for t in types:
            type_ids.append(self.env['project.task.type'].jira_dict(t).id)
        project_dict['type_ids'] = [(6, 0, type_ids)]
        # print("\n\n===============",project_dict)
        project = self.search([('key', '=', project_dict['key'])])
        if not project:
            project = self.create(project_dict)
        else:
            project.write(project_dict)

        return project

    def key_operation(self, key):
        project = self.search([('key', '=', key)])
        if not project:
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                project = self.process_response(company_id.get('project/' + key).json())
        return project

    def get_jira_id(self, id):
        project = self.search([('jira_id', '=', id)])
        if not project:
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                project = self.process_response(company_id.get('project/' + id).json())

        return project

    @api.depends('key')
    def name_get(self):
        result = []
        for project in self:
            if project.key:
                result.append((project.id, '[' + project.key + '] ' + project.name))
            else:
                result.append((project.id, project.name))
        return result

    jira_id = fields.Char()
    key = fields.Char()
    description = fields.Text()
    url = fields.Char()
    user_id = fields.Many2one(default=False)
    project_type_id = fields.Many2one('jira.type')
    project_template_id = fields.Many2one('jira.project.template')
    category_id = fields.Many2one('jira.category')
    issue_type_ids = fields.Many2many('issue.type', string='Issue Types')
    jira_project = fields.Boolean(default=True)
