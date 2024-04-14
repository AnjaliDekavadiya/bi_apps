# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.account'

    total_progress_billing = fields.Float(string="Total Progress Billing")
