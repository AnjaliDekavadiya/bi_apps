# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaskChecklistLine(models.Model):
    _name = 'task.checklist.line.custom'
    _description = 'Event Checklist Line'
    _order = 'sequence'

    checklist_id = fields.Many2one(
        'event.checklist.custom',
        string='Checklist',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence'
    )
    description = fields.Text(
        string='Description'
    )
    status = fields.Selection(
        [('pending','New'),
        ('done','Finished')],
        string='Status',
        default='pending',
        copy=False,
        readonly=True,
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        copy=False,
    )

    def action_custom_checklist_done(self):
        self.status = 'done'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: