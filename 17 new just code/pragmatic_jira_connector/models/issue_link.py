# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import warnings, UserError


class JiraIssueLinkSingle(models.Model):
    _name = 'jira.issue.link.single'
    _description = 'Jira Issue Link Single'

    @api.model
    def create(self, vals):
        ilinks = list()
        if not vals['link_id']:
            link = self.env['jira.link'].browse(vals['link_name'])
            link_type = self.env['jira.issue.link.type'].search(
                ['|', ('inward', '=', link.id), ('outward', '=', link.id)])

            if self.search([('link_name', '=', vals['link_name']), ('task_id', '=', vals['task_id'])]):
                raise UserError(_('Duplicate link'))

            if link.type == 'inward':
                inward_issue_id = vals['linked_task_id']
                outward_issue_id = vals['task_id']
                second_link = link_type.outward
            else:
                inward_issue_id = vals['task_id']
                outward_issue_id = vals['linked_task_id']
                second_link = link_type.inward

            issue_link = self.env['jira.issue.link'].create(dict(
                type_id=link_type.id,
                inward_issue_id=inward_issue_id,
                outward_issue_id=outward_issue_id
            ))

            vals['link_id'] = issue_link.id

            self.create(dict(
                link_name=second_link.id,
                task_id=vals['linked_task_id'],
                linked_task_id=vals['task_id'],
                link_id=issue_link.id
            ))

            issue = self.env['project.task'].browse(vals['task_id'])
            try:
                company_id = None
                user_id = self.env['res.users'].search([])
                for c_id in user_id.company_ids:
                    if c_id.account_id:
                        company_id = c_id
                if company_id:
                    ilinks = company_id.get('issue/' + issue.key + '?fields=issuelinks').json()['fields']['issuelinks']
            except Exception as e:
                raise UserError(_('Before Linking, please import this task to Jira!  ' + str(e)))

        linksingle = super(JiraIssueLinkSingle, self).create(vals)

        for l in ilinks:
            self.env['jira.issue.link'].process_response(issue, l)

        return linksingle

    link_name = fields.Many2one('jira.link', required=1)
    task_id = fields.Many2one('project.task', ondelete='cascade')
    linked_task_id = fields.Many2one('project.task', ondelete='cascade')
    link_id = fields.Many2one('jira.issue.link')
    jira_id = fields.Char(related='link_id.jira_id')


class JiraIssueLink(models.Model):
    _name = 'jira.issue.link'
    _description = 'Jira Issue Link'

    def create_jira_dict(self, vals, type):
        jira_dict = dict(
            type=dict(
                name=self.type_id.name,
            ),
            inwardIssue=dict(
                key=self.inward_issue_id.key,
            ),
            outwardIssue=dict(
                key=self.outward_issue_id.key,
            )
        )
        return jira_dict

    @api.model
    def create(self, vals):
        issue_link = super(JiraIssueLink, self).create(vals)
        if 'disable_mail_mail' not in self.env.context:
            issue_dict = issue_link.create_jira_dict(vals, 'CREATE')
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                response = company_id.post('issueLink', issue_dict)
        return issue_link

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
                    company_id.delete('issueLink/' + jira_id)
        return super(JiraIssueLink, self).unlink()

    def process_response(self, issue, response):
        link_dict = dict(
            jira_id=response['id'],
            type_id=self.env['jira.issue.link.type'].process_response(response['type']).id,
        )
        if 'inwardIssue' in response:
            link_dict['inward_issue_id'] = self.env['project.task'].key_operation(response['inwardIssue']['key']).id
            link_dict['outward_issue_id'] = issue.id
        if 'outwardIssue' in response:
            link_dict['inward_issue_id'] = issue.id
            link_dict['outward_issue_id'] = self.env['project.task'].key_operation(response['outwardIssue']['key']).id
        # link = self.search([('jira_id', '=', link_dict['jira_id'])])
        link = self.search([
            ('type_id', '=', link_dict['type_id']),
            ('inward_issue_id', '=', link_dict['inward_issue_id']),
            ('outward_issue_id', '=', link_dict['outward_issue_id']),
        ])
        if not link:
            link = self.create(link_dict)
        else:
            link.write(link_dict)

        link.single_link_ids.unlink()
        self.env['jira.issue.link.single'].create(dict(
            link_name=link.outward.id,
            task_id=link.inward_issue_id.id,
            linked_task_id=link.outward_issue_id.id,
            link_id=link.id
        ))
        self.env['jira.issue.link.single'].create(dict(
            link_name=link.inward.id,
            task_id=link.outward_issue_id.id,
            linked_task_id=link.inward_issue_id.id,
            link_id=link.id
        ))

        return link

    jira_id = fields.Char()
    type_id = fields.Many2one('jira.issue.link.type', required=1)
    inward = fields.Many2one('jira.link', required=1, related='type_id.inward')
    outward = fields.Many2one('jira.link', required=1, related='type_id.outward')
    inward_issue_id = fields.Many2one('project.task', ondelete='cascade')
    outward_issue_id = fields.Many2one('project.task', ondelete='cascade')
    single_link_ids = fields.One2many('jira.issue.link.single', 'link_id')


class JiraIssueLinkType(models.Model):
    _name = 'jira.issue.link.type'
    _description = 'Jira Issue Link Type'

    def create_jira_dict(self, vals, type):
        jira_dict = dict()
        if 'name' in vals:
            jira_dict['name'] = vals['name']
        if 'inward' in vals:
            jira_dict['inward'] = self.env['jira.link'].browse(vals['inward']).name
        if 'outward' in vals:
            jira_dict['outward'] = self.env['jira.link'].browse(vals['outward']).name
        return jira_dict

    @api.model
    def create(self, vals):
        issue_link_type = super(JiraIssueLinkType, self).create(vals)
        if 'disable_mail_mail' not in self.env.context and not issue_link_type.jira_id:
            issue_dict = issue_link_type.create_jira_dict(vals, 'CREATE')
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                response = company_id.post('issueLinkType', issue_dict)
                issue_link_type.jira_id = response.json()['id']
        return issue_link_type

    def write(self, vals):
        if 'disable_mail_mail' not in self.env.context:
            issue_dict = self.create_jira_dict(vals, 'WRITE')
            if issue_dict:
                company_id = None
                user_id = self.env['res.users'].search([])
                for c_id in user_id.company_ids:
                    if c_id.account_id:
                        company_id = c_id
                if company_id:
                    company_id.put('issueLinkType/' + self.jira_id, issue_dict)
        return super(JiraIssueLinkType, self).write(vals)

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
                    company_id.delete('issueLinkType/' + jira_id)
        return super(JiraIssueLinkType, self).unlink()

    def receive_all(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            response = company_id.get('issueLinkType').json()
            for jilt in response['issueLinkTypes']:
                self.process_response(jilt)

    def process_response(self, response):
        link_type_dict = dict(
            jira_id=response['id'],
            name=response['name'],
            inward=self.env['jira.link'].get_object(response['inward'], 'inward').id,
            outward=self.env['jira.link'].get_object(response['outward'], 'outward').id,
        )
        link_type = self.search([('jira_id', '=', link_type_dict['jira_id'])])
        if not link_type:
            link_type = self.create(link_type_dict)
        else:
            link_type.write(link_type_dict)
        return link_type

    jira_id = fields.Char()
    name = fields.Char(required=1)

    inward = fields.Many2one('jira.link', required=1)
    outward = fields.Many2one('jira.link', required=1)


class JiraLink(models.Model):
    _name = 'jira.link'
    _description = 'Jira Link'

    def get_object(self, name, type):
        name_object = self.search([('name', '=', name), ('type', '=', type)])
        if not name_object:
            name_object = self.create(dict(name=name, type=type))
        return name_object

    @api.model
    def create(self, vals):
        link = super(JiraLink, self).create(vals)
        if link.type == 'outward' and self.search([('name', '=', link.name), ('type', '=', 'inward')]):
            link.show = False
        return link

    name = fields.Char(required=1)
    type = fields.Selection([('inward', 'inward'), ('outward', 'outward')], required=1)
    show = fields.Boolean(default=True)
