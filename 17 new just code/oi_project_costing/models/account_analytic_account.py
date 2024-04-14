'''
Created on Apr 22, 2019

@author: Zuhair Hammadi
'''
from odoo import models, fields, api, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    project_costing_ids = fields.One2many('project.costing', 'analytic_id', copy=True)
    project_section_costing_ids = fields.One2many('project.costing', 'analytic_id', copy=False, domain=[('display_type', '=', 'line_section')])

    plan_amount = fields.Float('Plan Amount', compute='_calc_costing_amount')
    actual_amount = fields.Float('Actual Amount', compute='_calc_costing_amount')
    
    costing_category_ids = fields.Many2many('project.costing.category', compute='_calc_costing_category_ids')
    project_line_ids = fields.One2many('account.analytic.line', 'account_id', string="Project Analytic Lines")
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", store=True, compute_sudo=True)        
    
    @api.depends('project_costing_ids.plan_amount', 'project_costing_ids.actual_amount')
    def _calc_costing_amount(self):
        for record in self:
            line_ids = record.mapped('project_costing_ids').filtered(lambda line: not line.display_type)
            record.plan_amount = sum(line_ids.mapped('plan_amount'))
            record.actual_amount = sum(line_ids.mapped('actual_amount'))
            
    @api.depends('project_costing_ids')
    def _calc_costing_category_ids(self):
        for record in self:
            record.costing_category_ids = record.mapped("project_costing_ids.category_id").sorted()
    
    def action_project_costing(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Costing'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(self.env.ref('oi_project_costing.view_analytic_project_costing').id, 'form')],
            'context': {
                'project_costing': True
                }    
            }            
    
    def name_get(self):
        if self._context.get('project_costing'):
            res = []
            for analytic in self:
                res.append((analytic.id, _('Costing')))
            return res
        return super(AccountAnalyticAccount, self).name_get()
