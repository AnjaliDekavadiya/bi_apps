# -*- coding: utf-8 -*

from odoo import models, fields, api , _

class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    machine_repair_support_id = fields.Many2one(
        'machine.repair.support', 
        string="Machine Repair Request",
        required= True 
    )
    

    # @api.multi
    # def action_submit_expenses(self):
    #     res = super(HrExpense, self).action_submit_expenses()
    #     machine_repair_id = self.mapped('machine_repair_support_id')
        
    #     if machine_repair_id:
    #         machine_repair_support_id = machine_repair_id[0]
    #         # res['context'].update({
    #         #      'default_machine_repair_support_id': machine_repair_support_id.id
    #         #      })
    #         res.update({
    #              'default_machine_repair_support_id': machine_repair_support_id.id
    #              })
    #         self.machine_repair_support_id = machine_repair_support_id.id
    #     return res
    
    
    # def _create_sheet_from_expenses(self):
    def _get_default_expense_sheet_values(self):
        res = super(HrExpense, self)._get_default_expense_sheet_values()
        if self.mapped('machine_repair_support_id'):
            machine_repair_id = self.mapped('machine_repair_support_id')
            res[0].update({'machine_repair_support_id': machine_repair_id.id})
        return res