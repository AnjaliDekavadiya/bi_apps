# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from dateutil import parser
from datetime import date
import html2text
from odoo.exceptions import warnings, UserError, ValidationError
from bs4 import BeautifulSoup
import datetime
class JiraIssue(models.Model):
    _inherit = 'project.task'

    @api.depends('issue_type_id', 'issue_type_id.name')
    def compute_is_epic(self):
        for iss_id in self:
            if iss_id.issue_type_id and iss_id.issue_type_id.name == 'Epic':
                iss_id.is_epic = True
            elif iss_id.issue_type_id and iss_id.issue_type_id.name == 'Sub-task':
                iss_id.is_subtask = True
            elif iss_id.issue_type_id and iss_id.issue_type_id.name in ['Bug', 'Story', 'Task']:
                iss_id.is_subtask = False

    jira_id = fields.Char()
    key = fields.Char()
    planned_hours = fields.Datetime()
    jira_create = fields.Datetime(string='Created [JIRA]')
    jira_update = fields.Datetime(string='Updated [JIRA]')
    creator_id = fields.Many2one('res.users', string='Creator')
    reporter_id = fields.Many2one('res.users', string='Reporter')
    user_ids = fields.Many2many(default=False)
    issue_type_id = fields.Many2one('issue.type')
    priority_id = fields.Many2one('issue.priority')
    is_epic = fields.Boolean(compute=compute_is_epic, store=True)
    is_subtask = fields.Boolean(compute=compute_is_epic, store=True)
    link_ids = fields.One2many('jira.issue.link.single', 'task_id')
    jira_project = fields.Boolean(related='project_id.jira_project')
    issue_type_ids = fields.Many2many(related='project_id.issue_type_ids')

    def create_jira_dict(self, type):
        jira_dict = dict(
            fields=dict()
        )

        if self.project_id and type == 'CREATE':
            jira_dict['fields']['project'] = dict(id=self.env['project.project'].browse(self.project_id.id).jira_id)
        if self.name:
            jira_dict['fields']['summary'] = self.name
        if self.issue_type_id:
            jira_dict['fields']['issuetype'] = dict(id=self.env['issue.type'].browse(self.issue_type_id.id).jira_id)
        if self.description:
            jira_dict['fields']['description'] = html2text.html2text(self.description)
        if self.user_ids:
            # print("self.user_ids==================",self.user_ids)
            jira_dict['fields']['assignee'] = dict(id=self.env['res.users'].browse(self.creator_id.id).jira_accountId)
        if self.reporter_id:
            jira_dict['fields']['reporter'] = dict(id=self.env['res.users'].browse(self.reporter_id.id).jira_accountId)
        if self.priority_id:
            jira_dict['fields']['priority'] = dict(id=self.env['issue.priority'].browse(self.priority_id.id).jira_id)
        if self.tag_ids:
            tag_list = list()
            for t in self.tag_ids:
                tag_list.append(t.name)
            jira_dict['fields']['labels'] = tag_list

        if self.stage_id and type == 'WRITE':
            stage_obj = self.env['project.task.type'].browse(self.stage_id.id)
            if not stage_obj.jira_id:
                raise UserError(_('Selected stage must be connected to jira'))
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                response = company_id.get('issue/' + self.key + '/transitions').json()
                allowed_transitions = dict()
                for t in response['transitions']:
                    allowed_transitions[int(t['to']['id'])] = int(t['id'])
                if int(stage_obj.jira_id) not in allowed_transitions:
                    raise ValidationError(_('Unallowed transition'))
                response = company_id.post('issue/' + self.key + '/transitions',
                                           dict(transition=dict(id=allowed_transitions[int(stage_obj.jira_id)])))

        if self.parent_id:
            jira_dict['fields']['parent'] = dict(key=self.env['project.task'].browse(self.parent_id.id).key)

        return jira_dict

    def unlink(self):
        # print("\n\n\n============unlink------------")
        for j_id in self:
            # print("j_id============",j_id)
            jira_id = j_id.jira_id
            if jira_id:
                company_id = None
                user_id = self.env['res.users'].search([])
                for c_id in user_id.company_ids:
                    if c_id.account_id:
                        company_id = c_id
                if company_id:
                    company_id.delete('issue/' + jira_id)
        return super(JiraIssue, self).unlink()

    def receive_all(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            response = company_id.getall(
                'search?includeInactive=True&fields=*all&validateQuery=strict&jql=ORDER BY updatedDate asc')
            for resp in response:
                for r in resp:
                    self.process_response(r, True)
                    self.env.cr.commit()

    def latest_jira_issue_update(self):
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            response = company_id.getall(
                'search?includeInactive=True&fields=*all&validateQuery=strict&jql=updatedDate >= "-1d" ORDER BY updatedDate asc')
            for resp in response:
                for r in resp:
                    self.process_response(r, True)
                    self.env.cr.commit()

    def record_update(self):

        if self.project_id.jira_project and not self.jira_id:
            issue_dict = self.create_jira_dict('CREATE')
            # print("issue_dict------------------------ffffffffffffffffff",issue_dict)
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                response = company_id.post('issue', issue_dict)
                # print("response===============",response,response.text)
                self.write(dict(
                    jira_id=response.json()['id'],
                    key=response.json()['key']
                ))
            #
            if self.stage_id:
                self.write(dict(stage_id=self.stage_id.id))

            self = self.with_context(dict(disable_mail_mail=True))
            self.process_response(company_id.get('issue/' + self.jira_id).json())

        if self.project_id.jira_project and self.jira_id:
            issue_dict = self.create_jira_dict('WRITE')
            if issue_dict['fields']:
                company_id = None
                user_id = self.env['res.users'].search([])
                for c_id in user_id.company_ids:
                    if c_id.account_id:
                        company_id = c_id
                if company_id:
                    response = company_id.put('issue/' + self.jira_id, issue_dict)

        if self.jira_id:
            attachment_ids = self.env['ir.attachment'].search(
                [('res_id', '=', self.id), ('res_model', '=', 'project.task')])

            for attachment_id in attachment_ids:
                if attachment_id and not attachment_id.jira_id:
                    filepath = self.env['ir.attachment']._filestore() + '/' + attachment_id.store_fname
                    company_id = None
                    user_id = self.env['res.users'].search([])
                    for c_id in user_id.company_ids:
                        if c_id.account_id:
                            company_id = c_id
                    if company_id:
                        response = company_id.post_file(
                            'issue/' + self.jira_id + '/attachments',
                            filename=attachment_id.name, filepath=filepath)
                        attachment_id.jira_id = response.json()[0]['id']

        if self.key:
            comment_ids = self.env['mail.message'].search(
                [('res_id', '=', self.id), ('model', '=', 'project.task'), ('message_type', '=', 'comment')])

            if comment_ids:
                for comment_id in comment_ids:
                    soup = BeautifulSoup(comment_id.body, 'html.parser')
                    text_without_tags = soup.get_text("\n")
                    if text_without_tags:
                        data = {"body": text_without_tags}
                    if (data and self.key) and not comment_id.jira_id:
                        company_id = None
                        user_id = self.env['res.users'].search([])
                        for c_id in user_id.company_ids:
                            if c_id.account_id:
                                company_id = c_id
                        if company_id:
                            response = company_id.post('issue/' + self.key + '/comment',
                                                       data, )
                            comment_id.jira_id = response.json()['id']

    def process_response(self, response, update=False):
        issue = self.search([('key', '=', response['key'])])
        if issue:
            if issue.jira_update == fields.Datetime.to_string(parser.parse(response['fields']['updated'])):
                # print('SKIP')
                return issue
        if response['fields']['created']:
            jira_create_date = parser.parse(response['fields']['created']).strftime("%Y-%m-%d %H:%M:%S")
            jira_create_date = parser.parse(jira_create_date)
        if response['fields']['updated']:
            jira_update = parser.parse(response['fields']['updated']).strftime("%Y-%m-%d %H:%M:%S")
            jira_update = parser.parse(jira_update)
        issue_dict = dict(
            jira_id=response['id'],
            key=response['key'],
            name=response['fields']['summary'],
            issue_type_id=self.env['issue.type'].jira_dict(response['fields']['issuetype']).id,
            project_id=self.env['project.project'].key_operation(response['fields']['project']['key']).id,
            jira_create=jira_create_date,
            jira_update=jira_update,
            priority_id=False,
            user_ids=False,
            stage_id=self.env['project.task.type'].jira_dict(response['fields']['status']).id,
            # description=False,
            creator_id=self.env['res.users'].get_user_by_dict(response['fields']['creator']).id,
            partner_id=self.env['res.users'].get_user_by_dict(response['fields']['reporter']).partner_id.id,
            reporter_id=self.env['res.users'].get_user_by_dict(response['fields']['reporter']).id,
            parent_id=False,
            planned_hours=False,
            tag_ids=[(6, 0, [])],
        )
        if response['fields']['description']:
            issue_dict['description'] = response['fields']['description']
        if 'assignee' in response['fields'] and response['fields']['assignee']:
            assignee = self.env['res.users'].get_user_by_dict(response['fields']['assignee'])
            issue_dict['user_ids'] = [(6, 0, [assignee.id])]
        if 'priority' in response['fields'] and response['fields']['priority']:
            issue_dict['priority_id'] = self.env['issue.priority'].key_operation(
                response['fields']['priority']['id']).id
        if 'parent' in response['fields'] and response['fields']['parent']:
            issue_dict['parent_id'] = self.key_operation(response['fields']['parent']['key']).id
        if 'timeestimate' in response['fields'] and response['fields']['timeestimate']:
            issue_dict['planned_hours'] = response['fields']['timeestimate'] / 3600.0
        if response['fields']['labels']:
            tags = list()
            for l in response['fields']['labels']:
                tag = self.env['project.tags'].search([('name', '=', l)])
                if not tag:
                    tag = tag.create(dict(name=l))
                tags.append(tag.id)
            issue_dict['tag_ids'] = [(6, 0, tags)]

        issue = self.search([('key', '=', issue_dict['key'])])
        
        # print("\n\n\nissue_dict==================",issue_dict)
        if not issue:
            # print('Issue Get CREATE', jira_update, issue.key,)
            # del issue_dict['user_ids']
            issue = self.create(issue_dict)

        else:
            # pass
            
            # raise ValidationError(issue_dict)
            # del issue_dict['user_ids']
            issue.write(issue_dict)

        if update:
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                company_id.updated = jira_update.date()

        if response['fields']['comment']['total'] > response['fields']['comment']['maxResults']:
            int('a')
            self.env['mail.message'].receive_all(issue)
        else:
            for comment in response['fields']['comment']['comments']:
                self.with_context(dict(
                    disable_mail_mail=True
                )).env['mail.message'].process_response(issue, comment)
        company_id = None
        user_id = self.env['res.users'].search([])
        for c_id in user_id.company_ids:
            if c_id.account_id:
                company_id = c_id
        if company_id:
            for a in response['fields']['attachment']:
                self.env['ir.attachment'].while_import_attachemnt(issue, a)

        for l in response['fields']['issuelinks']:
            self.env['jira.issue.link'].process_response(issue, l)

        return issue

    def key_operation(self, key):
        issue = self.search([('key', '=', key)])
        if not issue:
            company_id = None
            user_id = self.env['res.users'].search([])
            for c_id in user_id.company_ids:
                if c_id.account_id:
                    company_id = c_id
            if company_id:
                issue = self.process_response(
                    company_id.get(
                        'search?includeInactive=True&fields=*all&validateQuery=strict&jql=key=' + key).json()['issues'][
                        0]
                )
        return issue

    @api.onchange('jira_project')
    def onchange_context(self):
        # print("\n\n\n\nhellooooooooooooooooooooooooooooooooooooo")
        if self.jira_project:
            if self.user_ids and not self.user_ids.jira_accountId:
                self.user_ids = False
            if self.reporter_id and not self.reporter_id.jira_accountId:
                self.reporter_id = False
            if self.creator_id and not self.creator_id.jira_accountId:
                self.creator_id = False
            return {'domain': {'user_ids': [('jira_accountId', '!=', False)],
                               'reporter_id': [('jira_accountId', '!=', False)],
                               'creator_id': [('jira_accountId', '!=', False)]}}
        else:
            return {'domain': {'user_ids': [],
                               'reporter_id': [],
                               'creator_id': []}}

    @api.depends('key')
    def name_get(self):
        result = []
        for issue in self:
            if issue.key:
                result.append((issue.id, '[' + issue.key + '] ' + issue.name))
            else:
                result.append((issue.id, issue.name))
        return result
