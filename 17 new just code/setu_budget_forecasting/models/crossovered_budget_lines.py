from odoo import fields, models, api


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    period_id = fields.Many2one(comodel_name='cash.forecast.fiscal.period',
                                string='Period',
                                related="crossovered_budget_id.period_id")

    year_id = fields.Many2one(comodel_name='cash.forecast.fiscal.year',
                              string='Year')
    percentage_ratio = fields.Float('Percentage Ratio', compute='_compute_percentage_ratio', store=True)

    @api.depends('planned_amount')
    def _compute_percentage_ratio(self):
        for line in self:
            line.percentage_ratio = 0.0
            if line.planned_amount:
                line.percentage_ratio = line.planned_amount * 100 / sum(
                    line.crossovered_budget_id.crossovered_budget_line.mapped('planned_amount'))

    @api.depends('crossovered_budget_id.period_id')
    def onchange_period_id(self):
        self.date_from = self.period_id.start_date
        self.date_to = self.period_id.end_date
