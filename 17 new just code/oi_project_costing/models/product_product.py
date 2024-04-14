'''
Created on Jul 29, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    costing_category_id = fields.Many2one('project.costing.category', string='Costing Category', compute = '_calc_costing_category_id')
    
    @api.depends('categ_id')
    def _calc_costing_category_id(self):
        for record in self:
            categ_id = record.categ_id
            costing_category_id = False
            while not costing_category_id and categ_id:
                costing_category_id = categ_id.costing_category_id
                categ_id = categ_id.parent_id
            record.costing_category_id = costing_category_id