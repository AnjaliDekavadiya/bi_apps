'''
Created on Feb 7, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Contract(models.Model):
    _inherit= 'hr.contract'

    schedule_id = fields.Many2one('hr.salary.schedule', string='Salary Schedule')
    grade_id = fields.Many2one('hr.salary.grade', tracking=True)
    step_id = fields.Many2one('hr.salary.step', tracking=True)
    salary = fields.Monetary(compute = '_calc_salary')
    
    schedule_type = fields.Selection(related='schedule_id.type')
    
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id.schedule_id:
            self.schedule_id = self.job_id.schedule_id
    
    @api.depends('grade_id', 'step_id')
    def _calc_salary(self):
        for record in self:
            record.salary = self.env['hr.salary.amount'].getAmount(record.grade_id, record.step_id)
            
    @api.onchange('grade_id')
    def _onchange_grade_id(self):
        if self.step_id and not self.step_id.grade_ids & self.grade_id:
            self.step_id = False
            
    @api.onchange('schedule_id')
    def _onchange_schedule_id(self):
        if self.step_id and self.step_id.schedule_id != self.schedule_id: 
            self.step_id = False                                
        if self.grade_id and self.grade_id.schedule_id != self.schedule_id: 
            self.grade_id = False            

    @api.constrains('schedule_id','grade_id','step_id')
    def _check_salary_schedule(self):
        for record in self:
            if record.grade_id and record.schedule_id and record.grade_id.schedule_id != record.schedule_id:
                raise ValidationError(_('Grade and schedule mismatch'))
            
            if record.step_id and record.schedule_id and record.step_id.schedule_id != record.schedule_id:
                raise ValidationError(_('Step and schedule mismatch'))
            
            if record.step_id and record.grade_id and not (record.grade_id & record.step_id.grade_ids):
                raise ValidationError(_('Step and grade mismatch'))
    
    @api.constrains('grade_id','wage')
    def _check_max_and_min_salary(self):
        for record in self:
            if record.grade_id and record.wage < record.grade_id.start_salary:
                raise ValidationError(_('Wage cannot be less than Grade Start Salary: %s.' % record.grade_id.start_salary))
            
            if record.grade_id and record.grade_id.schedule_type == 'grades_only' and record.wage > record.grade_id.end_salary:
                raise ValidationError(_('Wage cannot be greater than Grade End Salary: %s.' % record.grade_id.end_salary))
            
    @api.onchange('salary')
    def _onchange_salary(self):
        self.wage = self.salary