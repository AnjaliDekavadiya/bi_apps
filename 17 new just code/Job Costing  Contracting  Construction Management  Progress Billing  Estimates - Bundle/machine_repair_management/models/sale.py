# -*- coding: utf-8 -*

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    task_id = fields.Many2one(
        'project.task',
        string="Task",
    ) # This field is present in odoo Enterprice named industry_fsm 