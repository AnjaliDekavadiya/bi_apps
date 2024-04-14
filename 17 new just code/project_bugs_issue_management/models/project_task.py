# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

PROJECT_TASK_READABLE_FIELDS = {
    'custom_type',
    'custom_issues_type_id',
    'custom_repoter_id',
    'custom_environment',
    'custom_task_id',
    'custom_bugs_count',
}

class ProjectProject(models.Model):
    _inherit = 'project.project'

    custom_bugs_count = fields.Integer(compute='_custom_compute_bugs_count', string="Bugs/Issues Count")

    def _custom_compute_bugs_count(self):
        context = self.env.context or {}
        context = dict(context)
        context.update({'is_custom_bugs': True})
        task_data = self.env['project.task'].with_context(context).read_group([('project_id', 'in', self.ids), ('custom_type', '=', 'bugs_issues'), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['project_id'], ['project_id'])
        result = dict((data['project_id'][0], data['project_id_count']) for data in task_data)
        for project in self:
            project.custom_bugs_count = result.get(project.id, 0)

    def custom_action_view_bugs_issues(self):
        context = self.env.context or {}
        context = dict(context)
        context.update({'is_custom_bugs': True})
        for rec in self:
            bugs_ids = self.env['project.task'].with_context(context).search([
                ('project_id', '=', rec.id),
                ('custom_type', '=', 'bugs_issues')])
            action = self.env.ref('project_bugs_issue_management.custom_action_view_issues_bug').sudo().read()[0]
            action['domain'] = [('id', 'in', bugs_ids.ids)]
            return action

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS | PROJECT_TASK_READABLE_FIELDS

    custom_type = fields.Selection([
        ('task', 'Task'),
        ('bugs_issues', 'Bugs & Issues'),
        ], 
        string='Type', 
        default='task',
    )
    custom_issues_type_id = fields.Many2one(
        'custom.issues.type',
        string="Issue Type",
    )
    custom_repoter_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        string="Repoter"
    )
    custom_environment = fields.Html(
        string="Environment"
    )
    custom_task_id = fields.Many2one(
        'project.task',
        string = "Task"
    )
    custom_bugs_count = fields.Integer(compute='_custom_compute_bugs_count', string="Bugs/Issues Count")

    def _custom_compute_bugs_count(self):
        context = self.env.context or {}
        context = dict(context)
        context.update({'is_custom_bugs': True})
        task_data = self.env['project.task'].with_context(context).read_group([('custom_task_id', 'in', self.ids), ('custom_type', '=', 'bugs_issues'), '|', ('stage_id.fold', '=', False), ('stage_id', '=', False)], ['custom_task_id'], ['custom_task_id'])
        result = dict((data['custom_task_id'][0], data['custom_task_id_count']) for data in task_data)
        for task in self:
            task.custom_bugs_count = result.get(task.id, 0)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        context = self.env.context or {}
        if not context.get('is_custom_bugs'):
            domain.append((('custom_type', '=', 'task')))
            print('????????????????????????????',super(ProjectTask, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy))
        return super(ProjectTask, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)
    
    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     context = self.env.context or {}
    #     if not context.get('is_custom_bugs'):
    #         args.append((('custom_type', '=', 'task')))
    #     return super(ProjectTask, self)._search(args, offset, limit, order, count, access_rights_uid)

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     # context = self.env.context or {}
    #     # if not context.get('is_custom_bugs'):
    #     #     domain.append((('custom_type', '=', 'task')))
    #     return super(ProjectTask, self)._search(domain, offset, limit, order, access_rights_uid)

    def custom_action_view_bugs_issues(self):
        for rec in self:
            bugs_ids = self.env['project.task'].with_context({'is_custom_bugs': True}).search([
                ('custom_task_id', '=', rec.id),
                ('custom_type', '=', 'bugs_issues')])
            action = self.env.ref('project_bugs_issue_management.custom_action_view_task_issues_bug').sudo().read()[0]
            action['domain'] = [('id', 'in', bugs_ids.ids)]
            return action

    def _compute_access_url(self):
        super(ProjectTask, self)._compute_access_url()
        for task in self:
            task.access_url = '/my/project/custom_issues/%s' % task.id
