from odoo import api, fields, models


class BudgetPost(models.Model):
    _inherit = 'account.budget.post'

    cash_forecast_type = fields.Many2one(comodel_name='setu.cash.forecast.type', string='Cash Forecast Type')
