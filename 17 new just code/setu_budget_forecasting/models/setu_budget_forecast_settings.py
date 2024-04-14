from odoo import models, fields, api, _


class SetuBudgetForecastSettings(models.Model):
    _inherit = 'setu.budget.forecast.settings'

    auto_confirm_budget = fields.Boolean(string='Auto Confirm Budget')
    auto_validate_budget = fields.Boolean(string='Auto Validate Budget')
    auto_done_budget = fields.Boolean(string='Auto Done Budget')