'''
Created on Mar 15, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AppraisalPhase(models.Model):    
    _name = 'appraisal.phase'
    _inherit = ['appraisal.name.mixin']
    _description = 'Appraisal Phase'
    _order = 'sequence,id'
    
    sequence = fields.Integer()
