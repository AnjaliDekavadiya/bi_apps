'''
Created on Mar 30, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AppraisalQuestionGroup(models.Model):    
    _name = 'appraisal.question.group'
    _inherit = ['appraisal.name.mixin']
    _description = 'Appraisal Question Group'
    _order = 'sequence,id'
    
    sequence = fields.Integer()
    description = fields.Text(translate=True)    
    question_type = fields.Selection([('rating', 'Rating'),
                                      ('rating_objectives', 'Rating Objectives'),
                                      ('questions', 'Questions')], required=True)    
    rating_type_id = fields.Many2one('appraisal.rate', domain = [('type','=', 'question')])
    
    question_ids = fields.One2many('appraisal.question','question_group_id', copy = True)
        
    is_ad_hoc = fields.Boolean()