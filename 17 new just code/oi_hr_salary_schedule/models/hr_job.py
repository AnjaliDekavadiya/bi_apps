'''
Created on Feb 7, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class Job(models.Model):
    _inherit = 'hr.job'
    
    schedule_id = fields.Many2one('hr.salary.schedule', string='Salary Schedule')
    grade_ids = fields.Many2many('hr.salary.grade', string='Grades')