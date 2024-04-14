# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Project(models.Model):
    _inherit = "project.project"
    
    def _compute_notes_count(self):
        for project in self:
            project.notes_count = len(project.notes_ids)
            
    notes_ids = fields.One2many(
        'project.task', 
        'project_id', 
        string='Notes',
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count', 
        string="Notes"
    )
    
    # @api.multi #odoo13
    def view_notes(self):
        for rec in self:
            res = self.env.ref('project_task_notes.action_project_note_note_smart')
            res = res.sudo().read()[0]
            res['domain'] = str([('project_id','in',rec.ids)])
        return res
