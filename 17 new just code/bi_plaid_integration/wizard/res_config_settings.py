# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bi_plaid_client_id = fields.Char(string="Client ID", help=" Client ID")
    bi_plaid_secret_key = fields.Char(string="Secret Key", help="Secret Key")
    bi_plaid_environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('development', 'Development'),
        ('production', 'Production'),
    ], string="Environment", help="Plaid Environment")
    bi_plaid_access_token = fields.Char(string="Access Token", help="Access Token")
    bi_auto_bank_journal_id = fields.Many2one('account.journal', string='Journal', help="Bank Journal.",
                                              domain="[('type', '=', 'bank')]")
    bi_auto_bank_id = fields.Many2one('bi.plaid.bank.details', string='Plaid Bank', help="Plaid Bank.")
    bi_auto_transaction_start_date = fields.Datetime(string="Start Date", help="Transaction Start Date")
    bi_auto_plaid_account_ids = fields.Many2many(
        'bi.plaid.account.details', 'rel_plaid_account_details_transaction_auto', 'bi_plaid_account_id',
        'bi_plaid_auto_transaction_id',
        string="Plaid Accounts", help="Plaid Accounts")

    @api.onchange('bi_auto_bank_id')
    def _onchange_bi_auto_bank_id(self):
        plaid_bank = self.env['bi.plaid.bank.details'].browse(self.bi_auto_bank_id.id)
        self.bi_auto_bank_journal_id = plaid_bank.bi_auto_bank_journal_id.id
        self.bi_auto_transaction_start_date = plaid_bank.bi_auto_transaction_start_date
        self.bi_auto_plaid_account_ids = plaid_bank.bi_auto_plaid_account_ids
        self.bi_plaid_access_token = plaid_bank.bi_plaid_access_token
        res = {'domain': {'bi_auto_plaid_account_ids': [('bi_plaid_bank_id', '=', self.bi_auto_bank_id.id)]}}
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()

        bi_plaid_client_id = with_user.get_param('bi_plaid_integration.bi_plaid_client_id')
        bi_plaid_secret_key = with_user.get_param('bi_plaid_integration.bi_plaid_secret_key')
        bi_plaid_environment = with_user.get_param('bi_plaid_integration.bi_plaid_environment')

        res.update(
            bi_plaid_client_id=bi_plaid_client_id,
            bi_plaid_secret_key=bi_plaid_secret_key,
            bi_plaid_environment=bi_plaid_environment,
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param('bi_plaid_integration.bi_plaid_client_id',
                                                         self.bi_plaid_client_id)
        self.env['ir.config_parameter'].sudo().set_param('bi_plaid_integration.bi_plaid_secret_key',
                                                         self.bi_plaid_secret_key)
        self.env['ir.config_parameter'].sudo().set_param('bi_plaid_integration.bi_plaid_environment',
                                                         self.bi_plaid_environment)
        plaid_bank = self.env['bi.plaid.bank.details'].browse(self.bi_auto_bank_id.id)
        plaid_bank.write({
            'bi_auto_bank_journal_id': self.bi_auto_bank_journal_id.id,
            'bi_auto_transaction_start_date': self.bi_auto_transaction_start_date,
            'bi_plaid_access_token': self.bi_plaid_access_token,
            'bi_auto_plaid_account_ids': [(6, 0, self.bi_auto_plaid_account_ids.ids)],
        })
        return res
