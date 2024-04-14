'''
Created on May 3, 2023

@author: Zuhair Hammadi
'''
from odoo import models, fields

class AppraisalBatchType(models.Model):    
    _name = 'appraisal.batch.type'
    _description = 'Appraisal Batch Type'
    _inherit = ['appraisal.name.mixin']
        
    domain = fields.Text('Domain', default="[]")
    model_id = fields.Many2one('ir.model', domain = [('model','in', ['hr.employee', 'hr.contract'])], string='Applies to')
    model = fields.Char(related='model_id.model')
    