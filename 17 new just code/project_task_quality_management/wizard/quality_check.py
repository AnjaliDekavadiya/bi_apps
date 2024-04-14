# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class QualityCheckWizard(models.TransientModel):
    
    _name = "quality.check.wizard"
    _description = "Quality Check"


#    task_id = fields.Many2one(
#        'project.task',
#        string="Task",
#        required=True
#    )
#    project_id = fields.Many2one(
#        'project.project',
#        string="Project",
#        required=True
#    )
    team_id = fields.Many2one(
        'project.quality.team',
        string='Team',
        required=True
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        readonly=True, 
        default=lambda self: self.env.user.company_id
    )
    control_point_id = fields.Many2one(
        'project.quality.control.point',
        string='Control Point',
        required=True
    )
    check_user_id = fields.Many2one(
        'res.users',
        string='Checked By',
        required=True,
    )

    @api.onchange('project_id')
    def onchange_project_id(self):
        if self.project_id:
            if self.project_id != self.task_id.project_id:
                self.task_id = False
            return {'domain': {
                'task_id': [('project_id', '=', self.project_id.id)]
            }}
            
    @api.onchange('control_point_id')
    def _onchange_control_point_id(self):
        for check in self:
            check.team_id = check.control_point_id.team_id.id
            check.check_user_id = check.control_point_id.responsible_user_id.id

    #@api.multi
    def action_create_quality_check(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_id = context.get('active_ids')
        if active_id :
            project_task_id = self.env['project.task'].browse(active_id)
            vals = {
                 'task_id': project_task_id.id,
                 'project_id': project_task_id.project_id.id,
                 'team_id': self.team_id.id,
                 'company_id': self.company_id.id,
                 'control_point_id': self.control_point_id.id,
                 'check_user_id' : self.check_user_id.id,
                 'check_date' : fields.Date.today(),
            }
            quality_check = self.env['project.quality.check'].create(vals)
            action = self.env.ref('project_task_quality_management.action_project_quality_check').sudo().read()[0]
            action['domain'] = [('id','=',quality_check.id)]
            return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:       .
