# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    upsell_history_id = fields.One2many(
        'contract.upsell.history',
        'analytic_account_id',
        string='Contract Upsell History',
        copy=False,
    )

    #@api.multi
    def open_upsell_quotations(self):
        self.ensure_one()
        action = self.env.ref("sale.action_quotations_with_onboarding").read([])[0]
        action['domain'] = [('analytic_account_id', '=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
