'''
Created on Apr 26, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AppraisalQuestionSelection(models.Model):    
    _name = 'appraisal.question.selection'
    _description = 'Appraisal Question Selection'
    _order='sequence,id'
        
    question_id = fields.Many2one('appraisal.question', required = True, ondelete='cascade')
    name = fields.Char(required = True)
    sequence = fields.Integer()    
    
    
    