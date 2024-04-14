# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class HREntryChecklist(models.Model):
    _name = 'hr.entry.checklist'
    _description = 'Employee Checklist'

    name = fields.Char(required=True)
    description = fields.Text()


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    entry_checklist = fields.Many2many('hr.entry.checklist', 'employee_checklist_rel', 'checklist_id', 'employee_id', 'Entry Checklist', default=0.0)
    check_marked = fields.Float('Entry Progress', compute='_compute_check_marked', store=True, digits="2")
    max_value = fields.Float(default=100.0)

    @api.depends('entry_checklist')
    def _compute_check_marked(self):
        all_checklist = self.env['hr.entry.checklist'].search([])
        if len(all_checklist) >=1 : 
            for rec in self:
                selected_checklist = rec.entry_checklist
                rec.check_marked = (len(selected_checklist)* 100)/len(all_checklist)
