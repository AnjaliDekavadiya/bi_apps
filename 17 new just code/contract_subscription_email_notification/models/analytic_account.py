# -*- coding: utf-8 -*-

import datetime
from datetime import date, timedelta as td
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    reminder_date = fields.Date(
        compute = '_compute_reminder_date',
        string = "Reminder Date",
        copy = False,
        store = True
    )

    @api.depends('end_date','number_of_days')
    def _compute_reminder_date(self):
        for rec in self:
            if rec.end_date:
                new_date = datetime.timedelta(days=rec.number_of_days)
                rec.reminder_date = rec.end_date - new_date

    @api.model
    def _cron_contract_expiry_reminder(self):
        # contracts = self.env['account.analytic.account'].search([('reminder_date','=',fields.Date.today())])
        contracts = self.env['account.analytic.account'].search([('reminder_date','=',fields.Date.context_today(self))])
        for contract in contracts:
            template = self.env.ref('contract_subscription_email_notification.email_template_contract_subscription_expiring_soon')
            template.send_mail(contract.id)

    
    # @api.multi #odoo13
    def write(self, vals):
        res = super(AccountAnalyticAccount, self).write(vals)
        for rec in self:
            if rec.stage == 'inprogress':
                template = self.env.ref('contract_subscription_email_notification.email_template_contract_subscription_running')
                template.send_mail(rec.id)
            if rec.stage == 'expired':
                template = self.env.ref('contract_subscription_email_notification.email_template_contract_subscription_expired')
                template.send_mail(rec.id)
        return res
