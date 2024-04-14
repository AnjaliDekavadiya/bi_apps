'''
Created on Oct 31, 2018

@author: Zuhair Hammadi
'''
from odoo import models, fields

class HRAttributeSelection(models.Model):
    _name = "hr.attribute.selection"
    _description = "Employee Attribute Selection"
    _order = 'name'

    name = fields.Char('Value', required = True)    

    attribute_id = fields.Many2one('hr.attribute', required = True)
    
    
    _sql_constraints = [
        ('uk_name', 'unique(attribute_id, name)', 'Name must be unique!')
        ]    