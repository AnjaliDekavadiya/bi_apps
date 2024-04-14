# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import plaid
from datetime import datetime
from odoo import fields, models
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions


class BiPlaidBankDetails(models.Model):
    _name = 'bi.plaid.bank.details'
    _description = "Bi Plaid Bank Details"

    name = fields.Char(string="Bank Name", help="Name of Bank associated with Plaid")
    bi_plaid_account_ids = fields.One2many(
        'bi.plaid.account.details',
        'bi_plaid_bank_id',
        string=" Accounts",
        help="Plaid Accounts")
    bi_plaid_status = fields.Selection([
        ('connected', 'Connected'),
        ('not_connected', 'Not Connected'),
    ], string="Status", help="Status", default="not_connected")
    bi_auto_bank_journal_id = fields.Many2one('account.journal', string='Journal', help="Bank Journal.",
                                              domain="[('type', '=', 'bank')]")
    bi_auto_transaction_start_date = fields.Datetime(string="Start Date", help="Transaction Start Date")
    bi_auto_plaid_account_ids = fields.Many2many(
        'bi.plaid.account.details', 'rel_bi_plaid_account_details_transaction_auto', 'bi_plaid_account_id',
        'bi_plaid_auto_transaction_id',
        string="Plaid Accounts", help="Plaid Accounts")
    bi_plaid_access_token = fields.Char(string="Access Token", help="Access Token")

    def get_plaid_account_details(self, bank_id):
        plaid_bank_obj = self.env['bi.plaid.bank.details'].browse(bank_id)
        with_user = self.env['ir.config_parameter'].sudo()
        bi_plaid_access_token = with_user.get_param('bi_plaid_integration.bi_plaid_access_token')
        plaid_bank_obj.bi_plaid_access_token = bi_plaid_access_token

        try:
            accounts_request = AccountsGetRequest(
                access_token=bi_plaid_access_token
            )
            client = self.get_plaid_configuration()
            accounts_response = client.accounts_get(accounts_request)
            self.create_plaid_account(accounts_response.to_dict(), bank_id)

            plaid_bank_obj.bi_plaid_status = "connected"
        except plaid.ApiException as e:
            response = json.loads(e.body)
            return json.dumps({'error': {'status_code': e.status, 'display_message':
                response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}})
        return True

    def create_plaid_account(self, account_response, bank_id):
        bi_plaid_account_obj = self.env['bi.plaid.account.details']
        for account_res in account_response.get('accounts'):
            plaid_acc_exist = bi_plaid_account_obj.search([
                ('bi_plaid_account_id', '=', account_res.get('account_id')),
                ('bi_plaid_bank_id', '=', bank_id)
            ])
            if not plaid_acc_exist:
                bi_plaid_account_obj.create({
                    'name': account_res.get('name'),
                    'bi_plaid_account_id': account_res.get('account_id'),
                    'bi_plaid_account_type': account_res.get('type'),
                    'bi_plaid_account_subtype': account_res.get('subtype'),
                    'bi_plaid_bank_id': bank_id
                })
        return True

    def get_environment_url(self):
        with_user = self.env['ir.config_parameter'].sudo()
        bi_plaid_environment = with_user.get_param('bi_plaid_integration.bi_plaid_environment')

        if bi_plaid_environment == "sandbox":
            url = "https://sandbox.plaid.com"
        elif bi_plaid_environment == "development":
            url = "https://development.plaid.com"
        elif bi_plaid_environment == "production":
            url = "https://plaid.com"
        return url

    def get_plaid_configuration(self):
        with_user = self.env['ir.config_parameter'].sudo()
        bi_plaid_client_id = with_user.get_param('bi_plaid_integration.bi_plaid_client_id')
        bi_plaid_secret_key = with_user.get_param('bi_plaid_integration.bi_plaid_secret_key')
        configuration = plaid.Configuration(
            host=self.get_environment_url(),
            api_key={
                'clientId': bi_plaid_client_id,
                'secret': bi_plaid_secret_key
            }
        )
        api_client = plaid.ApiClient(configuration)
        client = plaid_api.PlaidApi(api_client)
        return client

    def auto_get_plaid_transactions(self):
        acc_bnk_state_obj = self.env['account.bank.statement']
        bi_plaid_transactions_obj = self.env['bi.plaid.transactions']

        plaid_banks = self.env['bi.plaid.bank.details'].search([('bi_plaid_status', '=', 'connected')])
        for plaid_bank in plaid_banks:
            bi_plaid_access_token = plaid_bank.bi_plaid_access_token
            bi_auto_bank_journal_id = plaid_bank.bi_auto_bank_journal_id
            bi_auto_transaction_start_date = plaid_bank.bi_auto_transaction_start_date
            bi_auto_plaid_account_ids = plaid_bank.bi_auto_plaid_account_ids
            client = self.env['bi.plaid.bank.details'].get_plaid_configuration()
            request = TransactionsGetRequest(
                access_token=bi_plaid_access_token,
                start_date=datetime.date(bi_auto_transaction_start_date),
                end_date=datetime.date(datetime.now()),
                options=TransactionsGetRequestOptions(
                    account_ids=bi_auto_plaid_account_ids.mapped('bi_plaid_account_id')
                )
            )
            response = client.transactions_get(request)
            transactions = response['transactions']
            # Manipulate the count and offset parameters to paginate
            # transactions and retrieve all available data
            while len(transactions) < response['total_transactions']:
                request = TransactionsGetRequest(
                    access_token=bi_plaid_access_token,
                    start_date=datetime.date(datetime.strptime(bi_auto_transaction_start_date, "%Y-%m-%d %H:%M:%S")),
                    end_date=datetime.date(datetime.now()),
                    options=TransactionsGetRequestOptions(
                        account_ids=bi_auto_plaid_account_ids.mapped('bi_plaid_account_id'),
                        offset=len(transactions)
                    )
                )
                response = client.transactions_get(request)
                transactions.extend(response['transactions'])
            if transactions:
                bank_stat_name = bi_auto_bank_journal_id.name + " statement " + datetime.now().strftime("%Y/%m/%d")
                line_vals = bi_plaid_transactions_obj.prepare_bank_statement_line_vals(transactions)
                acc_bnk_state_obj.create({
                    'name': bank_stat_name,
                    'journal_id': bi_auto_bank_journal_id.id,
                    'line_ids': line_vals
                })
            plaid_bank.bi_auto_transaction_start_date = datetime.now()
        return True
