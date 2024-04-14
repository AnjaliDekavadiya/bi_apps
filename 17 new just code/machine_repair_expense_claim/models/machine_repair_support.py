# -*- coding: utf-8 -*

from odoo import models, fields, api , _

class MachineRepairSupport(models.Model):
    _inherit = 'machine.repair.support'
    
    expense_sheet_count = fields.Integer(
        compute='_compute_expense_sheet_counter',
        string="Expense Sheet Count"
    )

    def _compute_expense_sheet_counter(self):
        for rec in self:
            rec.expense_sheet_count = self.env['hr.expense.sheet'].search_count(
                [('machine_repair_support_id','=', self.id)]
            )

    #@api.multi
    def show_hr_expense_sheet(self):
        self.ensure_one()
        # for rec in self:
            # res = self.env.ref('hr_expense.action_hr_expense_sheet_my_all')
        # res = res.sudo().read()[0]
        res = self.env["ir.actions.actions"]._for_xml_id("hr_expense.action_hr_expense_sheet_my_all")
        res['domain'] = ([('machine_repair_support_id','=',self.id)])
        return res
    
