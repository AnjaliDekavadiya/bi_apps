'''
Created on Feb 7, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class SalaryStep(models.Model):
    _name = 'hr.salary.step'
    _description = 'Salary Step'
    _order = 'sequence,name,id'
        
    schedule_id = fields.Many2one('hr.salary.schedule', required = True, string= 'Salary Schedule', ondelete = 'cascade')
    name = fields.Char(required = True)
    sequence = fields.Integer()
    
    index = fields.Integer(compute = '_calc_index')
    grade_ids = fields.Many2many('hr.salary.grade', compute = '_calc_grade_ids', search = '_search_grade_ids')
    
    _sql_constraints= [
            ('name_unqiue', 'unique(schedule_id, name)', 'Name must be unique!'),
        ]    
    
    @api.depends('sequence')
    def _calc_index(self):
        for record in self:
            record.index = record.schedule_id.step_ids.ids.index(record.id)
            # record.index = 1
            
    @api.depends('schedule_id')
    def _calc_grade_ids(self):
        for step in self:
            grade_ids = step.schedule_id.grade_ids
            for grade in list(grade_ids):
                if grade.start_step_id and grade.start_step_id.index > step.index:
                    grade_ids -= grade
                if grade.end_step_id and grade.end_step_id.index < step.index:
                    grade_ids -= grade
            step.grade_ids = grade_ids
            
    def _search_grade_ids(self, operator, value):
        grade_ids = self.env['hr.salary.grade'].search([('id', operator, value)])
        step_ids = grade_ids.mapped('schedule_id.step_ids')
        for step in list(step_ids):
            if not step.grade_ids & grade_ids:
                step_ids -=step
        return [('id', 'in', step_ids.ids)]

    def _next_step(self, grade_id):
        self.ensure_one()
        if isinstance(grade_id, int):
            grade_id = self.env['hr.salary.grade'].browse(grade_id)
        next_step_id = self.schedule_id.step_ids.filtered(lambda step : step.index > self.index)[:1]
        if grade_id not in next_step_id.grade_ids:
            return self.browse()
        return next_step_id