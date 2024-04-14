'''
Created on Feb 7, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SalaryAmount(models.Model):
    _name = 'hr.salary.amount'
    _description = 'Salary Schedule Amount'
    
    schedule_id = fields.Many2one('hr.salary.schedule', required = True, string= 'Salary Schedule', ondelete = 'cascade')
    grade_id = fields.Many2one('hr.salary.grade', required = True, ondelete = 'cascade')
    step_id = fields.Many2one('hr.salary.step', required = True, ondelete = 'cascade')
    amount = fields.Float(group_operator = 'avg')
    
    _sql_constraints= [
            ('uk', 'unique(grade_id, step_id)', 'Grade/Step must be unique!'),
        ]        
    
    @api.constrains('schedule_id', 'grade_id', 'step_id')
    def _check_data(self):
        for record in self:
            assert record.schedule_id == record.grade_id.schedule_id
            assert record.schedule_id == record.step_id.schedule_id
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError(_('Amount must be positive'))
    
    @api.model
    def getAmount(self, grade_id, step_id):
        if isinstance(grade_id, models.BaseModel):
            grade_id = grade_id.id
        if isinstance(step_id, models.BaseModel):
            step_id = step_id.id            
        record = self.search([('grade_id','=', grade_id), ('step_id','=', step_id)])
        return record.amount