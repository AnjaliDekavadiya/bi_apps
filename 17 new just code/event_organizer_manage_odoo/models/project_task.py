# -*- coding: utf-8 -*-

from odoo import models, fields

class Project(models.Model):
    _inherit = 'project.project'

    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False,
    )

class ProjectTask(models.Model):
    _inherit = 'project.task'

    event_checklistline_ids = fields.One2many(
        'task.checklist.line.custom',
        'task_id',
        string='Checklist Lines',
        copy=False,
    )
    event_custom_id = fields.Many2one(
        'event.event',
        copy=False,
        string='Event',
    )
    
    


