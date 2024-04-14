'''
Created on Mar 30, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AppraisalEvaluationTemplateLine(models.Model):    
    _name = 'appraisal.evaluation.template.line'
    _description = 'Appraisal Evaluation Template Line'
    _order = 'sequence,id'
    
    sequence = fields.Integer()
    evaluation_template_id = fields.Many2one('appraisal.evaluation.template', required=True, ondelete = 'cascade')
    question_group_id = fields.Many2one('appraisal.question.group', required=True)
    weight = fields.Float()
    
    extra = fields.Boolean()