'''
Created on Jul 28, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    timesheet_product_id = fields.Many2one('product.product', string='Timesheet Product')