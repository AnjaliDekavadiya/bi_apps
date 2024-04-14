# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    project_stage_security_ids = fields.One2many(
        'project.stage.security',
        'security_id',
    )

class ProjectStageSecurity(models.Model):
    _name = 'project.stage.security'
    _description ='Project Stage Security'
    
    security_id = fields.Many2one(
        'project.project'
    )        
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
         required=True,
    )
    group_ids = fields.Many2many(
        'res.groups',
        string='Responsible Groups'
    )
    stage_id = fields.Many2one(
        'project.task.type',
        string='Stage',
        required=True,
    )
