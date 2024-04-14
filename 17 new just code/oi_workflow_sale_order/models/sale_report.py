'''
Created on Jun 17, 2021

@author: Jaber Ali
'''
from odoo import models, api, fields

class SaleReport(models.Model):
    _inherit = "sale.report"
    
    @api.model
    def _get_state(self):
        return self.env['sale.order']._get_state()
    
    state = fields.Selection(_get_state)