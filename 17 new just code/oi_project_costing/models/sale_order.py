'''
Created on Apr 22, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, _, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    plan_amount = fields.Float(related='analytic_account_id.plan_amount')
        
    def action_project_costing(self):
        if not self.analytic_account_id:
            raise UserError(_('Please set the analytic account'))
        return self.analytic_account_id.action_project_costing()
        
    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        record = super(SaleOrder, self).copy(default = default)
        if self.analytic_account_id.project_costing_ids:
            if self.name in self.analytic_account_id.name:
                name = self.analytic_account_id.name.replace(self.name, record.name)
            else:
                name = "%s: %s" % (self.analytic_account_id.name, record.name)
            record.analytic_account_id = self.analytic_account_id.copy(default = dict(name = name))
        return record