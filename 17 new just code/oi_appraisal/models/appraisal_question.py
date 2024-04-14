'''
Created on Mar 30, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AppraisalQuestion(models.Model):    
    _name = 'appraisal.question'
    _description = 'Appraisal Question'
    _order = 'sequence,id'
    
    question_group_id = fields.Many2one('appraisal.question.group', string='Question Group', required=True, ondelete='cascade')
    question_type = fields.Selection(related='question_group_id.question_type')
    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer()
    
    widget = fields.Selection([('char', 'Single Line Text'), 
                               ('text', 'Multiple Lines Text'), 
                               ('float', 'Number'), 
                               ('selection', 'Selection (Drop Down)'),
                               ('radio', 'Selection (Radio)')
                               ])
    
    selection_ids = fields.One2many('appraisal.question.selection', 'question_id')
    
    optional = fields.Boolean()
    
    weight = fields.Float(default = 1)
    
    computed = fields.Boolean()
    compute_code = fields.Text()