# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api,_

class ProjectRiskTask(models.TransientModel):
    _name = 'project.project.risk.incident'
    _description = 'project.project.risk.incident'

    @api.model
    def _default_project(self):
        #project_task = self.env['project.task'].browse(self._context.get('active_id'))
        project_task = self.env['project.project'].browse(self._context.get('active_id'))
        if project_task:
            #return project_task.project_id.id
            return project_task.id
    
    risk_task_image = fields.Binary(
        'Incident Photo', 
    )
    description = fields.Text(
        string='Description',
        required=True
    )
    name = fields.Char(
        string='Risk Incident', 
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        default=_default_project,
        required=True
    )
  

    # @api.multi
    def create_project_risk_incedent(self):
        self.ensure_one()
        # for rec in self:
        #     active_id = rec._context.get('active_id')
        #     task_vals = {
        #     'name':rec.name,
        #     'project_id': rec.project_id.id,
        #     'is_task_incident':True,
        #     'image':rec.risk_task_image,
        #     'description':rec.description,
        #     }
        #     task = self.env['project.task'].create(task_vals)
        

        # active_id = self._context.get('active_id')
        task_vals = {
        'name':self.name,
        'project_id': self.project_id.id,
        'is_task_incident':True,
        'image':self.risk_task_image,
        'description':self.description,
        }
        task = self.env['project.task'].create(task_vals)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
   

     
        
