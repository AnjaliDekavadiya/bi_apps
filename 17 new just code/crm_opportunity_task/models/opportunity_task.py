# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class CrmLead(models.Model):
    _inherit = "crm.lead"

    custom_task_ids = fields.Many2many(
        'project.task',
        string='Tasks',
        readonly=True
    )
    task_count = fields.Integer(
        compute='_compute_task_counter',
        string="Task Count",
    )

    def _compute_task_counter(self):
        for rec in self:
            rec.task_count = self.env['project.task'].search_count(
                [('custom_crm_lead_id', 'in', rec.ids)])

    # def action_view_task(self):
    #     for rec in self:
    #         action = self.env.ref(
    #             'project.action_view_task').sudo().read()[0]
    #         action['domain'] = [(
    #             'custom_crm_lead_id', 'in', rec.ids)]
    #         return action

    def action_view_task(self):
        self.ensure_one()

        list_view_id = self.env.ref('project.view_task_tree2').id
        form_view_id = self.env.ref('project.view_task_form2').id

        action = {'type': 'ir.actions.act_window_close'}
        task_projects = self.custom_task_ids.mapped('project_id')
        if len(task_projects) == 1 and len(self.custom_task_ids) > 1:  # redirect to task of the project (with kanban stage, ...)
            action = self.with_context(active_id=task_projects.id).env['ir.actions.actions']._for_xml_id(
                'project.act_project_project_2_project_task_all')
            action['domain'] = [('id', 'in', self.custom_task_ids.ids)]
            if action.get('context'):
                eval_context = self.env['ir.actions.actions']._get_eval_context()
                eval_context.update({'active_id': task_projects.id})
                action_context = safe_eval(action['context'], eval_context)
                action_context.update(eval_context)
                action['context'] = action_context
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
            action['context'] = {}  # erase default context to avoid default filter
            if len(self.custom_task_ids) > 1:  # cross project kanban task
                action['views'] = [[False, 'kanban'], [list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'calendar'], [False, 'pivot']]
                action['domain'] = [('custom_crm_lead_id', 'in', self.ids)]

            elif len(self.custom_task_ids) == 1:  # single task -> form view
                action['views'] = [(form_view_id, 'form')]
                action['res_id'] = self.custom_task_ids.id
        # filter on the task of the current SO
        # action.setdefault('context', {})
        # action['context'].update({'search_default_sale_order_id': self.id})
        return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
