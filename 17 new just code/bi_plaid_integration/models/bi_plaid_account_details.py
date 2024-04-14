# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BiPlaidAccountDetails(models.Model):
    _name = 'bi.plaid.account.details'
    _description = "Bi Plaid Account Details"

    name = fields.Char(string="Account Name", help="Name of Bank Account associated with Plaid")
    bi_plaid_account_type = fields.Char(string="Account Type", help="Plaid Account Type")
    bi_plaid_account_subtype = fields.Char(string="Account Subtype", help="Plaid Account Subtype")
    bi_plaid_account_id = fields.Char(string="Account ID", help="Plaid Account ID")
    bi_plaid_bank_id = fields.Many2one(
        'bi.plaid.bank.details', string="Plaid Bank", help="Plaid Bank", ondelete='cascade')


