from odoo import api, fields, models


class BudgetComparisonWizard(models.Model):
    _name = 'budget.comparison.wizard'

    comparison_for = fields.Selection([
        ('fiscal_year', 'Fiscal Years'),
        ('fiscal_period', 'Fiscal Periods')], default='fiscal_year', string='Budget Comparison For')
    fiscal_year_ids = fields.Many2many('cash.forecast.fiscal.year', string="Fiscal Years")
    fiscal_period_ids = fields.Many2many('cash.forecast.fiscal.period', string="Fiscal Periods")

    def calculate_value(self):
        tree_view_id = self.env.ref('setu_budget_forecasting.setu_view_crossovered_budget_calculation_tree').id
        pivot_view_id = self.env.ref('setu_budget_forecasting.setu_view_crossovered_budget_calculation_pivot').id
        graph_view_id = self.env.ref('setu_budget_forecasting.setu_view_crossovered_budget_calculation_graph').id
        if self.fiscal_year_ids:
            budgets = self.env['crossovered.budget'].search([('year_id', 'in', self.fiscal_year_ids.ids)])
        elif self.fiscal_period_ids:
            budgets = self.env['crossovered.budget'].search([('period_id', 'in', self.fiscal_period_ids.ids)])
        domain = [('crossovered_budget_id', 'in', budgets.ids)]
        return {
            'name': 'Budgets Comparison',
            'type': 'ir.actions.act_window',
            'res_model': 'crossovered.budget.lines',
            'view_mode': 'pivot,graph,tree',
            'views': [(pivot_view_id, 'pivot'), (graph_view_id, 'graph'), (tree_view_id, 'tree')],
            'res_id': False,
            'target': 'self',
            'domain': domain,
        }
