'''
Created on Jul 29, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = "product.category"
    
    costing_category_id = fields.Many2one('project.costing.category', string='Costing Category')    