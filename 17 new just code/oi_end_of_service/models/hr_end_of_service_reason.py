'''
Created on Oct 24, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class EndOfServiceReason(models.Model):
    _name = 'hr.end_of_service.reason'
    _description = _name
    _order = 'name'
    
    name = fields.Char(required=True, translate = True)
    code = fields.Char()
    
    _sql_constraints= [
            ('name_unqiue', 'unique(name)', 'Name must be unique!')
        ]    
    