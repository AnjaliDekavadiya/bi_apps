from odoo import fields, models, api, _
import json
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    period_id = fields.Many2one(comodel_name='cash.forecast.fiscal.period',
                                string='Period_id')
    year_id = fields.Many2one(comodel_name='cash.forecast.fiscal.year',
                              string='Year')
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')

    def _kanban_dashboard_graph(self):
        for data in self:
            data.kanban_dashboard_graph = json.dumps(data.get_bar_graph_datas())

    def get_bar_graph_datas(self):
        record = self.env['crossovered.budget'].search(
            [('period_id', '=', self.period_id.id), ('name', '=', self.name)])
        result = []
        for data in record:
            for line in data.crossovered_budget_line:
                result.append(
                    {'label': line.general_budget_id.name, 'value': line.planned_amount, 'type': 'future'})
        data = [{'label': '21-27 Aug', 'value': 33337.5, 'type': ''}, ]
        if not result.__len__():
            return [{'values': data, 'title': "dummy"}]
        if all(d['value'] == 0.0 for d in result):
            return [{'values': data, 'title': "zero-dummy"}]
        else:
            return [{'values': result, 'title': "graph_title"}]

    def open_action(self):
        return {
            'name': _('Budgets'),
            'view_mode': 'form',
            'res_model': 'crossovered.budget',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }

    @api.onchange('period_id')
    def onchange_period_id(self):
        self.date_from = self.period_id.start_date
        self.date_to = self.period_id.end_date
        self.year_id = self.period_id.fiscal_id

    @api.onchange('year_id')
    def onchange_year_id(self):
        self.date_from = self.year_id.start_date
        self.date_to = self.year_id.end_date
        self.period_id = False

    def create_budget_from_cash_forecast(self):
        active_model = self._context.get('active_model')
        if active_model == 'cash.forecast.fiscal.year':
            budget_type = 'yearly'
        else:
            budget_type = 'periodically'

        records = self.env[active_model].browse(self._context.get('active_ids', []))
        for record in records:
            vals = {'name': record.code,
                    'user_id': self.env.uid,
                    'period_id': budget_type == 'periodically' and record.id or False,
                    'year_id': budget_type == 'yearly' and record.id or False,
                    'company_id': record.company_id.id,
                    'date_from': record.start_date,
                    'date_to': record.end_date
                    }

            line_vals = []
            if budget_type == 'yearly':
                domain = [('forecast_period_id', 'in', record.fiscal_period_ids.ids)]
                budget_domain = [('year_id', '=', record.id)]
            else:
                domain = [('forecast_period_id', '=', record.id)]
                budget_domain = [('period_id', '=', record.id)]

            budget_posts = self.env['account.budget.post'].search([('company_id', '=', record.company_id.id)])
            for budget_post in budget_posts:
                cash_forecast = self.env['setu.cash.forecast'].search(domain +
                                                                      [('forecast_type_id', '=',
                                                                        budget_post.cash_forecast_type.id)])
                planned_amount = sum(cash_forecast.mapped('forecast_value'))
                line_vals.append((0, 0, {
                    'general_budget_id': budget_post.id,
                    'analytic_account_id': budget_post.cash_forecast_type.analytic_account_id.id,
                    'period_id': budget_type == 'periodically' and record.id or False,
                    'year_id': budget_type == 'yearly' and record.id or False,
                    'paid_date': record.end_date,
                    'date_from': record.start_date,
                    'date_to': record.end_date,
                    'planned_amount': planned_amount
                }))
            vals['crossovered_budget_line'] = line_vals
            if budget := self.search(budget_domain + [('company_id', '=', record.company_id.id)]):
                budget.write({'crossovered_budget_line': [(6, 0, [])]})
                budget.write(vals)
            else:
                self.create(vals)
        return {
            'name': 'Budgets',
            'type': 'ir.actions.act_window',
            'res_model': 'crossovered.budget',
            'view_mode': 'kanban,tree,form',
            'views': [(self.env.ref('setu_budget_forecasting.kanban_crossovered_budget_view').id, 'kanban')],
            'target': 'current',
        }

    @api.model
    def get_dashboard_data(self):

        today_date = datetime.now().date()
        previous_year_date = str(today_date - relativedelta(years=1))
        next_year_date = str(today_date + relativedelta(years=1))

        result = {
            "Chart_1": {
                "label": [],
                "data": {
                    "Planned Amount": [],
                    "Practical Amount": []
                }
            },
            "Chart_2": {
                "label": [],
                "data": {
                    str(today_date.year - 1): [],
                    str(today_date.year): [],
                    str(today_date.year + 1): [],
                }
            }
        }

        current_year_data = self.env['crossovered.budget'].search(
            [('date_from', '<', today_date), ('date_to', '>', today_date)])
        previous_year_data = self.env['crossovered.budget'].search(
            [('date_from', '<', previous_year_date), ('date_to', '>', previous_year_date)])
        next_year_data = self.env['crossovered.budget'].search(
            [('date_from', '<', next_year_date), ('date_to', '>', next_year_date)])

        result["Chart_1"]["label"] = current_year_data.crossovered_budget_line.mapped('general_budget_id').mapped(
            'name')
        result["Chart_1"]["data"]["Planned Amount"] = current_year_data.crossovered_budget_line.mapped('planned_amount')
        result["Chart_1"]["data"]["Practical Amount"] = current_year_data.crossovered_budget_line.mapped(
            'practical_amount')

        result["Chart_2"]["label"] = current_year_data.crossovered_budget_line.mapped('general_budget_id').mapped(
            'name')
        result["Chart_2"]["data"][str(today_date.year - 1)] = self.convert_to_percentage(
            previous_year_data.crossovered_budget_line.mapped('percentage'), result)
        result["Chart_2"]["data"][str(today_date.year)] = self.convert_to_percentage(
            current_year_data.crossovered_budget_line.mapped('percentage'), result)
        result["Chart_2"]["data"][str(today_date.year + 1)] = self.convert_to_percentage(
            next_year_data.crossovered_budget_line.mapped('percentage'), result)

        return result

    def convert_to_percentage(self, data, input_dict):
        try:
            if not data:
                new_data_length = input_dict["Chart_2"]["data"][str(datetime.now().date().year)].__len__() or input_dict["Chart_2"]["data"][str(datetime.now().date().year - 1)].__len__() or input_dict["Chart_2"]["data"][str(datetime.now().date().year + 1)].__len__()
                new_data = []
                for data in range(new_data_length):
                    new_data.append(0)
                return new_data
            result = [value * 100 for value in data]
        except Exception:
            return data
        return result
