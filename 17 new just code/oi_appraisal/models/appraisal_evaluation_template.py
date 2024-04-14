'''
Created on Mar 27, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AppraisalEvaluationTemplate(models.Model):    
    _name = 'appraisal.evaluation.template'
    _inherit = ['appraisal.name.mixin']
    _description = 'Appraisal Evaluation Template'
    _order = 'sequence,id'
    
    sequence = fields.Integer()
    line_ids = fields.One2many('appraisal.evaluation.template.line','evaluation_template_id', copy = True)