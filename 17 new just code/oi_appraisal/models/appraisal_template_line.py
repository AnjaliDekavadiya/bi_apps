'''
Created on Mar 30, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AppraisalTemplateLine(models.Model):    
    _name = 'appraisal.template.line'
    _description = 'Appraisal Template Evaluation'
    _order = 'sequence,id'
    
    sequence = fields.Integer()
    active= fields.Boolean(default=True)
    template_id = fields.Many2one('appraisal.template', required=True, ondelete = 'cascade')
    name = fields.Char(required=True)    
    evaluation_template_id = fields.Many2one('appraisal.evaluation.template', required=True)
    weight = fields.Float()
    evaluator_field_id = fields.Many2one('ir.model.fields', string='Evaluator', domain=[('model','=','hr.employee'),('ttype','like','many'),('relation','=','hr.employee'),('name','!=','subordinate_ids')])    