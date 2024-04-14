# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class QualityAlertWizard(models.TransientModel):
    _name = "quality.alert.wizard"
    _description = "Quality Alert"


    title = fields.Char(
        string= 'Title',
        required= True
    )
  
    #@api.multi
    def action_create_quality_alert(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_id = context.get('active_ids')
        if active_id :
            project_quality_check_id = self.env['project.quality.check'].browse(active_id)
            vals = {
                'title': self.title,
                'project_quality_check_id' : project_quality_check_id.id,
                'task_id': project_quality_check_id.task_id.id,
                'project_id': project_quality_check_id.project_id.id,
                'team_id': project_quality_check_id.team_id.id,
                'responsible_user_id' : project_quality_check_id.check_user_id.id,
            }
            alert = self.env['project.quality.alert'].create(vals)
            action = self.env.ref('project_task_quality_management.action_project_quality_alert').sudo().read()[0]
            action['domain'] = [('id', '=', alert.id)]
            return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
