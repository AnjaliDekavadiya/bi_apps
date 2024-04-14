'''
Created on Feb 7, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _

class SalarySchedule(models.Model):
    _name = 'hr.salary.schedule'
    _description = 'Salary Schedule'
    
    name = fields.Char(required = True)
    code = fields.Char(required = True)
    description = fields.Text()
    active = fields.Boolean(default = True)
    
    grade_ids = fields.One2many('hr.salary.grade', 'schedule_id', string='Grades', copy = True)
    grade_count = fields.Integer(compute = '_calc_grade_count')
    step_ids = fields.One2many('hr.salary.step', 'schedule_id', string='Steps', copy = True)
    amount_ids = fields.One2many('hr.salary.amount', 'schedule_id', string='Amounts', copy = True)
    amount_count = fields.Integer(compute = '_calc_search_default')
    
    type = fields.Selection([('grades_only','Grades Only'),('grades_and_steps','Grades and Steps')],default='grades_and_steps')
    
    _sql_constraints= [
            ('name_unqiue', 'unique(name)', 'Name must be unique!'),
            ('code_unqiue', 'unique(code)', 'Code must be unique!'),
        ]    
    
    @api.depends('amount_ids')
    def _calc_search_default(self):
        for record in self:
            record.amount_count = len(record.amount_ids)
    
    @api.depends('grade_ids')
    def _calc_grade_count(self):
        for record in self:
            record.grade_count = len(record.grade_ids)
    
    def copy_data(self, default=None):
        default = default or {}
        if 'name' not in default:
            default['name'] =  _("%s (copy)") % (self.name or '')
        if 'code' not in default:
            default['code'] =  _("%s (copy)") % (self.code or '')            
        return super(SalarySchedule, self).copy_data(default = default)
        
    def action_amount(self):
        self.ensure_one()
        action, = self.env.ref("oi_hr_salary_schedule.act_hr_salary_amount").read([])
        action['domain'] = [('schedule_id', '=', self.id)]
        action['context'] = {
            'default_schedule_id' : self.id
            }
        return action
    
    def action_grade(self):
        self.ensure_one()
        action, = self.env.ref('oi_hr_salary_schedule.act_hr_salary_grade').read()
        action['domain'] = [('schedule_id', '=', self.id)]
        action['context'] = {
            'default_schedule_id' : self.id,
            }
        return action
        
    def generate_amounts(self):
        vals_list = []
        for grade in self.grade_ids:
            amount = grade.start_salary
            for step in self.step_ids:        
                if grade not in step.grade_ids:
                    continue
                if not self.env['hr.salary.amount'].getAmount(grade, step):
                    vals_list.append({
                        'grade_id' : grade.id,
                        'step_id' : step.id,
                        'amount' : amount,
                        'schedule_id': self.id
                    })
                amount += grade.increment
        self.env['hr.salary.amount'].create(vals_list)
        return self.action_amount()        