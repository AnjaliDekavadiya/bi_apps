# -*- coding: utf-8 -*

from odoo import models, fields, api

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    
    machine_repair_support_id = fields.Many2one(
        'machine.repair.support', 
        string="Machine Repair Request",
    )
    