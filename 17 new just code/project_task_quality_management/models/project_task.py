# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models  


class Task(models.Model):
    
    _inherit = "project.task"

    quality_check_count = fields.Integer(
        compute='_compute_quality_check_counter',
        string="Quality Check Count"
    )

    def _compute_quality_check_counter(self):
        for rec in self:
            rec.quality_check_count = self.env['project.quality.check'].search_count([('task_id', 'in', self.ids)])

    #@api.multi
    def action_button_quality_check(self):
        self.ensure_one()
        action = self.env.ref("project_task_quality_management.action_project_quality_check").read([])[0]
        action['domain'] = [('task_id','in',self.ids)]
        return action

class Project(models.Model):
    
    _inherit = "project.project"

    quality_check_count = fields.Integer(
        compute='_compute_quality_check_counter',
        string="Quality Check Count"
    )

    def _compute_quality_check_counter(self):
        for rec in self:
            rec.quality_check_count = self.env['project.quality.check'].search_count([('project_id', 'in', self.ids)])

    #@api.multi
    def action_button_quality_check(self):
        self.ensure_one()
        action = self.env.ref("project_task_quality_management.action_project_quality_check").read([])[0]
        action['domain'] = [('project_id','in',self.ids)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
