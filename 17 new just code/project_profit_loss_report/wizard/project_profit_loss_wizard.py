# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ProjectProfitLossWizard(models.TransientModel):
    _name = 'project.profit.loss.wizard'

    today = fields.date.today()
    end_date = today + relativedelta(day=1, months=+1, days=-1)
    start_date = today + relativedelta(day=1)
    
    custom_start_date = fields.Date(
        'Start Date',
        required=True,
        default=start_date,
    )
    custom_end_date = fields.Date(
        'End Date',
        required=True,
        default=end_date,
    )
    custom_analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        string='Analytic Account',
        required=True,
    )

    # @api.multi
    def get_project_profit_loss_report(self, data=None):
        data = self.sudo().read()[0]
        data.update({
            'analytic_account_ids': self.custom_analytic_account_ids.ids,
            'start_date': self.custom_start_date,
            'end_date': self.custom_end_date,
        })
        act = self.env.ref(
            'project_profit_loss_report.project_profit_loss_report_probc'
            ).report_action(self, data=data)
        return act

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
