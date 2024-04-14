# -*- coding: utf-8 -*-

import json
import plaid
from datetime import datetime
from odoo import fields, models, api, _
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from odoo.exceptions import UserError


class BiPlaidTransactions(models.TransientModel):
    _name = "bi.plaid.transactions"
    _description = "Get Plaid Transactions Wizard"

    bank_journal_id = fields.Many2one('account.journal', string='Journal', help="Bank Journal.", domain="[('type', '=', 'bank')]")
    plaid_bank_id = fields.Many2one('bi.plaid.bank.details', string='Plaid Bank', help="Plaid Bank.")
    transaction_start_date = fields.Datetime(string="Start Date", help="Transaction Start Date")
    transaction_end_date = fields.Datetime(string="End Date", help="Transaction End Date")
    plaid_account_ids = fields.Many2many(
        'bi.plaid.account.details', 'rel_plaid_account_details_transcation', 'bi_plaid_account_id', 'bi_plaid_transaction_id',
        string="Plaid Accounts", help="Plaid Accounts")


    @api.onchange('plaid_bank_id')
    def _onchange_bi_auto_bank_id(self):
        res = {'domain': {'plaid_account_ids': [('bi_plaid_bank_id', '=', self.plaid_bank_id.id)]}}
        return res

    def get_transactions(self):
        acc_bnk_state_obj = self.env['account.bank.statement']
        plaid_bank_obj = self.env['bi.plaid.bank.details'].browse(self.plaid_bank_id.id)
        bi_plaid_access_token = plaid_bank_obj.bi_plaid_access_token
        client = self.env['bi.plaid.bank.details'].get_plaid_configuration()
        try:
            request = TransactionsGetRequest(
                access_token=bi_plaid_access_token,
                start_date=datetime.date(self.transaction_start_date),
                end_date=datetime.date(self.transaction_end_date),
                options=TransactionsGetRequestOptions(
                    account_ids=self.plaid_account_ids.mapped('bi_plaid_account_id')
                )
            )
            response = client.transactions_get(request)
            transactions = response['transactions']
            # Manipulate the count and offset parameters to paginate
            # transactions and retrieve all available data
            while len(transactions) < response['total_transactions']:
                request = TransactionsGetRequest(
                    access_token=bi_plaid_access_token,
                    start_date=datetime.date(self.transaction_start_date),
                    end_date=datetime.date(self.transaction_end_date),
                    options=TransactionsGetRequestOptions(
                        account_ids=self.plaid_account_ids.mapped('bi_plaid_account_id'),
                        offset=len(transactions)
                    )
                )
                response = client.transactions_get(request)
                transactions.extend(response['transactions'])
        except plaid.ApiException as e:
            response = json.loads(e.body)
            res_err= json.dumps({'error': {'status_code': e.status, 'display_message':
                response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}})
            raise UserError(_("Can't get transactions from plaid. it gives below error. \n\n %s", res_err))

        if transactions:
            bank_stat_name = self.bank_journal_id.name + " statement " + datetime.now().strftime("%Y/%m/%d")
            line_vals = self.prepare_bank_statement_line_vals(transactions)
            acc_bnk_state_obj.create({
                'name': bank_stat_name,
                'journal_id': self.bank_journal_id.id,
                'line_ids': line_vals
            })
        return True

    def prepare_bank_statement_line_vals(self, transactions):
        bank_statement_line_vals = []
        for transaction in transactions:
            bank_statement_line_dict = {
                'payment_ref': transaction.get('name'),
                'amount': transaction.get('amount'),
                'date': datetime.date(datetime.now()),
                'journal_id': self.bank_journal_id.id,
            }
            bank_statement_line_vals.append((0, 0, bank_statement_line_dict))
        return bank_statement_line_vals
