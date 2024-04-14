# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ChecklistTemplateWizard(models.Model):
    _name = 'checklist.template.wizard.cust'
    _description = 'Checklist Template Wizard'
    
    checklist_template_custom_id = fields.Many2one(
        'checklist.template.custom',
        string='Checklist Template',
        required=True
    )

    def add_checklist_line_custom(self):
        self._add_checklist_line_custom()

    def _add_checklist_line_custom(self):
        self.ensure_one()
        checklist_line_obj = self.env['task.checklist.line.custom']
        task_id = self.env['project.task'].browse(self._context.get('active_id'))
        for line in self.checklist_template_custom_id.checklist_ids:
            checklist_line_obj.create({
                'checklist_id': line.id,
                'sequence': line.sequence,
                'task_id': task_id.id,
            })