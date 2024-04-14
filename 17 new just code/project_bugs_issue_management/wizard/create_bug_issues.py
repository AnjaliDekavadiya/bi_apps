# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ProjectBugsIssuesWizard(models.TransientModel):
    _name = "project.bugs.issues.wizard"

    @api.model
    def default_get(self, fields):
        res = super(ProjectBugsIssuesWizard, self).default_get(fields)
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and model == 'project.project':
            record = self.env[model].browse(active_id)
            res.update({
                'partner_id': record.partner_id.id,
                'company_id': record.company_id.id,
                'project_id': record.id,
            })
        if active_id and model == 'project.task':
            record = self.env[model].browse(active_id)
            res.update({
                'partner_id': record.partner_id.id,
                'company_id': record.company_id.id,
                'project_id': record.project_id.id,
                'task_id': record.id,
            })
        return res

    name = fields.Char(
        required=True,
        string="Issue Title"
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
    )
    company_id = fields.Many2one(
        'res.company', 
        string = 'Company',
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        required=True,
        default=lambda self: self.env.user,
        string="Assigned to"
    )
    project_id = fields.Many2one(
        'project.project',
        required=True,
        string="Project"
    )
    task_id = fields.Many2one(
        'project.task',
        domain="[('project_id', '=', project_id)]",
        string="Task"
    )
    description = fields.Html(
        required=True,
        string='Description'
    )
    custom_issues_type_id = fields.Many2one(
        'custom.issues.type',
        required=True,
        string="Issue Type",
    )
    custom_environment = fields.Html(
        string="Environment"
    )

    def custom_create_bugs_issues(self):
        vals = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'user_ids': self.user_id.ids,
            'project_id': self.project_id.id,
            'custom_task_id': self.task_id.id,
            'description': self.description,
            'custom_type': 'bugs_issues',
            'custom_repoter_id': self.env.user.id,
            'custom_issues_type_id': self.custom_issues_type_id.id,
            'custom_environment': self.custom_environment
        }
        task_id = self.env['project.task'].sudo().create(vals)
        print(',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,',task_id)
        action = self.env.ref("project.action_view_task").sudo().read()[0]
        action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
        action['res_id'] = task_id.id
        print('...........................................')
        return action