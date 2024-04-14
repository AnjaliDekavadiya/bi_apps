from odoo import fields, models, api


class SetuCashForecastType(models.Model):
    _inherit = 'setu.cash.forecast.type'

    def create_budget_post(self):
        account_budget_post = self.env['account.budget.post']
        records = self.filtered(lambda x: x.type in ['income', 'expense'])
        for record in records:
            values = {
                'name': record.name,
                'company_id': record.company_id.id,
                'account_ids': [(6, 0, record.account_ids.ids)],
                'cash_forecast_type': record.id
            }
            if budget_post := account_budget_post.search([('cash_forecast_type', '=', record.id)]):
                budget_post.write(values)
            else:
                budget_post.create(values)
        return True
