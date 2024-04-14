'''
Created on Jul 28, 2019

@author: Zuhair Hammadi
'''
from odoo import models, api

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    def _timesheet_preprocess(self, vals):
        vals = super(AccountAnalyticLine, self)._timesheet_preprocess(vals)
        for val in vals:
            if val.get('employee_id') and not val.get('product_id'):
                employee = self.env['hr.employee'].browse(val.get('employee_id'))
                val['product_id'] = employee.timesheet_product_id.id
        return vals
    
    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(AccountAnalyticLine, self).create(vals_list)
        ProjectCosting = self.env['project.costing'].sudo()
        for record in records:
            if record.amount < 0 and record.product_id.costing_category_id and not ProjectCosting.search([('analytic_id', '=', record.account_id.id), ('product_id', '=', record.product_id.id)], limit =1):
                ProjectCosting.create({
                    'name' : record.product_id.name,
                    'analytic_id' : record.account_id.id,
                    'product_id' : record.product_id.id,
                    'category_id' : record.product_id.costing_category_id.id,
                    'product_uom_id' : self.product_id.uom_id,
                    'plan_price' : self.product_id.standard_price,
                    'sequence' : 9999
                    })
            
        return records