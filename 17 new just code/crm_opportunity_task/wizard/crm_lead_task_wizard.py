# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class CrmLeadTaskWizard(models.TransientModel):
    _name = 'crm.lead.task.wizard'
    _description = 'crm.lead.task.wizard'

    @api.model
    def default_get(self, fields):
        rec = super(CrmLeadTaskWizard, self).default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        active_record = self.env[active_model].browse(active_id)
        rec.update({
            'partner_id': active_record.partner_id.id,
            'user_id': active_record.user_id.id,
            'name': active_record.name,
            'description': active_record.description,
        })
        return rec

    # @api.onchange('project_id')
    # def _onchange_project_id(self):
    #     for rec in self:
    #         stages = self.env['project.task.type'].search([('project_ids','in',rec.project_id.id)])
    #         for stage in stages:
    #             rec.stage_id = stage

    stage_id = fields.Many2one(
        'project.task.type',
        string='Stage',
        required=True,
        domain="[('project_ids','in',project_id)]"
    )
    name = fields.Char(
        string='Name',
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        copy=False,
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string="Assigned to",
    )
    date_deadline = fields.Date(
        string='Deadline',
    )
    tag_ids = fields.Many2many(
        'project.tags',
        string='Tags',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    description = fields.Char(
        string='Description'
    )
    date_assign = fields.Datetime(
        string='Assigning Date',
        default = str(fields.date.today()),
        index=True, 
        copy=False, 
    )

    # @api.multi
    def create_task(self):
        task_object = self.env['project.task']
        lead_id = self.env['crm.lead'].browse(
            self.env.context.get('active_id'))
        for rec in self:
            task_vals = {
                'project_id': rec.project_id.id,
                'company_id': rec.company_id.id,
                'name': rec.name,
                'user_ids': [(4, rec.user_id.id)],
                'date_deadline': rec.date_deadline,
                'tag_ids': [(6, 0, rec.tag_ids.ids)],
                'partner_id': rec.partner_id.id,
                'description': rec.description,
                'date_assign': rec.date_assign,
                'stage_id': rec.stage_id.id,
            }
            task_id = task_object.create(task_vals)
            task_id.custom_crm_lead_id = lead_id.id
            lead_id.custom_task_ids = [(4, t.id) for t in task_id]
        return lead_id.action_view_task()
        # return task_id.project_id.action_view_tasks()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

