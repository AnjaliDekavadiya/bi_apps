'''
Created on Feb 7, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class SalaryGrade(models.Model):
    _name = 'hr.salary.grade'
    _description = 'Salary Grade'
    _order = 'sequence,name,id'
    
    schedule_id = fields.Many2one('hr.salary.schedule', required = True, string= 'Salary Schedule', ondelete = 'cascade')
    name = fields.Char(required = True)
    code = fields.Char()
    sequence = fields.Integer()
    
    start_salary = fields.Float()
    end_salary = fields.Float()
    median_salary = fields.Float(compute="_calc_median_salary")
    increment = fields.Float()
    
    start_step_id = fields.Many2one('hr.salary.step', copy = False)
    end_step_id = fields.Many2one('hr.salary.step', copy = False)
    
    job_ids = fields.Many2many('hr.job', string='Job Positions')
    
    index = fields.Integer(compute = '_calc_index')
    schedule_type = fields.Selection(related='schedule_id.type')
    
    _sql_constraints= [
            ('name_unqiue', 'unique(schedule_id, name)', 'Name must be unique!'),
            ('code_unqiue', 'unique(schedule_id, code)', 'Code must be unique!'),
        ]
    
    @api.depends('start_salary','end_salary')
    def _calc_median_salary(self):
        for record in self:
            if record.schedule_id.type == 'grades_only':
                record.median_salary = (record.start_salary + record.end_salary) / 2
            else:
                record.median_salary = 0
                
    @api.depends('sequence')
    def _calc_index(self):
        for record in self:
            record.index = record.schedule_id.grade_ids.ids.index(record.id) if record.schedule_id.grade_ids else False
               
    def _next_grade(self, step_id):
        self.ensure_one()
        amount = self.env['hr.salary.amount'].getAmount(self,step_id)
        next_grade_id = self.schedule_id.grade_ids.filtered(lambda grade : grade.index > self.index)[:1]
        next_step_id = None
        for step_id in self.schedule_id.step_ids:
            new_amount = self.env['hr.salary.amount'].getAmount(next_grade_id,step_id)
            if new_amount > amount and next_grade_id in step_id.grade_ids :
                next_step_id = step_id
                break
        
        return next_grade_id, next_step_id