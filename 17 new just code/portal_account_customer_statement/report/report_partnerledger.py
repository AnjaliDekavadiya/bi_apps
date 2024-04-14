# -*- coding: utf-8 -*-

import time
from odoo import api, models


class ReportPartnerLedger_statement(models.AbstractModel):
    _inherit = 'report.account_customer_statement.report_partnerledger_custom'

#     def _lines(self, data, partner):
#         full_account = []
#         move_line_obj = self.env['account.move.line']
#         query_get_data = move_line_obj.with_context(
#             data['form'].get('used_context', {})
#         )._query_get()
#         print("query_get_data:-",query_get_data)
#         reconcile_clause = "" if data['form']['reconciled']\
#             else' AND "account_move_line".reconciled = false '
#         print("reconcile_clause",reconcile_clause)
#         params = [
#             partner.id,
#             tuple(data['computed']['move_state']),
#             tuple(data['computed']['account_ids'])
#         ] + query_get_data[2]
#         query = """
#             SELECT
#                 "account_move_line".id, "account_move_line".date,
#                 j.code, acc.code as a_code, acc.name as a_name,
#                 "account_move_line".ref, m.name as move_name,
#                 "account_move_line".name, "account_move_line".debit,
#                 "account_move_line".credit,
#                 "account_move_line".amount_currency,
#                 "account_move_line".currency_id,
#                 c.symbol AS currency_code
#             FROM
#                 """ + query_get_data[0] + """
#             LEFT JOIN
#                 account_journal j ON ("account_move_line".journal_id = j.id)
#             LEFT JOIN
#                 account_account acc
#             ON
#                 ("account_move_line".account_id = acc.id)
#             LEFT JOIN
#                 res_currency c ON ("account_move_line".currency_id=c.id)
#             LEFT JOIN
#                 account_move m ON (m.id="account_move_line".move_id)
#             WHERE
#                 "account_move_line".partner_id = %s
#                 AND
#                     m.state IN %s
#                 AND
#                     "account_move_line".account_id IN %s AND """ +\
#                 query_get_data[1] + reconcile_clause + """
#                 ORDER BY "account_move_line".date"""
#         self.env.cr.execute(query, tuple(params))
#         res = self.env.cr.dictfetchall()
#         sum = 0.0
#         for r in res:
#             r['displayed_name'] = '-'.join(
#                 r[field_name] for field_name in ('move_name', 'ref', 'name')
#                 if r[field_name] not in (None, '', '/')
#             )
#             sum += r['debit'] - r['credit']
#             r['progress'] = sum
#             if r['currency_id'] is None:
#                 r['currency_id'] = self.env.user.company_id.currency_id.id
#                 r['currency_code'] =\
#                     self.env.user.company_id.currency_id.symbol
#                 r['amount_currency'] = r['progress']
#             full_account.append(r)
#         return full_account

#     def _sum_partner(self, data, partner, field):
#         if field not in ['debit', 'credit', 'debit - credit']:
#             return
#         result = 0.0
#         move_line_obj = self.env['account.move.line']
#         query_get_data = move_line_obj.with_context(
#             data['form'].get('used_context', {})
#         )._query_get()
#         reconcile_clause = "" if data['form']['reconciled']\
#             else ' AND "account_move_line".reconciled = false '

#         params = [
#             partner.id,
#             tuple(data['computed']['move_state']),
#             tuple(data['computed']['account_ids'])
#         ] + query_get_data[2]
#         query = """SELECT sum(""" + field + """)
#                 FROM """ + query_get_data[0] + """, account_move AS m
#                 WHERE "account_move_line".partner_id = %s
#                     AND m.id = "account_move_line".move_id
#                     AND m.state IN %s
#                     AND account_id IN %s
#                     AND """ + query_get_data[1] + reconcile_clause
#         self.env.cr.execute(query, tuple(params))

#         contemp = self.env.cr.fetchone()
#         if contemp is not None:
#             result = contemp[0] or 0.0
#         return result

# #     @api.multi
# #     def render_html(self, doc_ids, data):
    @api.model
    def _get_report_values(self, docids, data=None):
        if self._context.get("from_portal_report"):
            parter_id = self.env.user.partner_id
            default_fields = [
                'reconciled',
                'result_selection',
                'journal_ids',
                'company_id',
                'date_to',
                'amount_currency',
                'target_move',
                'date_from'
            ]
            context = self.env.context.copy()
            context.update({
                'active_ids': parter_id.ids,
                'active_id': parter_id.id,
                'active_model': 'res.partner'
            })
            partnerledger_boj = self.env['account.report.partner.ledger.statement']
            partner_ledger_statement = partnerledger_boj.with_context(context)
            # get default values for wizard
            ledger_data = partner_ledger_statement.sudo().default_get(default_fields)
            ledger_data.update({'reconciled': True})
            # create wizard record using default values
            wizard_id = partner_ledger_statement.sudo().create(ledger_data)
            # make data dictionary to call report
            data = {}
            data['ids'] = parter_id.ids
            data['model'] = 'res.partner'
            data['form'] = wizard_id.read(default_fields)[0]
            data['form'].update({'custom_partner_ids': parter_id.ids})
            used_context = partner_ledger_statement._build_contexts(data)
            data['form']['used_context'] = dict(
                used_context, lang=context.get('lang') or 'en_US'
            )
        return super(ReportPartnerLedger_statement, self.sudo())._get_report_values(docids=docids, data=data)
#         data['computed'] = {}
#         obj_partner = self.env['res.partner']
#         query_get_data = self.env['account.move.line'].with_context(
#             data['form'].get('used_context', {})
#         )._query_get()
#         data['computed']['move_state'] = ['draft', 'posted']
#         if data['form'].get('target_move', 'all') == 'posted':
#             data['computed']['move_state'] = ['posted']
#         result_selection = data['form'].get('result_selection', 'customer')
#         if result_selection == 'supplier':
#             data['computed']['ACCOUNT_TYPE'] = ['payable']
#         elif result_selection == 'customer':
#             data['computed']['ACCOUNT_TYPE'] = ['receivable']
#         else:
#             data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

#         self.env.cr.execute("""
#             SELECT a.id
#             FROM account_account a
#             WHERE a.internal_type IN %s
#             AND NOT a.deprecated""", (
#             tuple(data['computed']['ACCOUNT_TYPE']),
#             ))
#         data['computed']['account_ids'] = [
#             a for (a,) in self.env.cr.fetchall()
#         ]
#         params = [
#             tuple(data['computed']['move_state']),
#             tuple(data['computed']['account_ids'])
#         ] + query_get_data[2]
#         reconcile_clause = "" if data['form']['reconciled']\
#             else ' AND "account_move_line".reconciled = false '
#         query = """
#             SELECT DISTINCT "account_move_line".partner_id
#             FROM """ + query_get_data[0] + """,
#                  account_account AS account, account_move AS am
#             WHERE "account_move_line".partner_id IS NOT NULL
#                 AND "account_move_line".account_id = account.id
#                 AND am.id = "account_move_line".move_id
#                 AND am.state IN %s
#                 AND "account_move_line".account_id IN %s
#                 AND NOT account.deprecated
#                 AND """ + query_get_data[1] + reconcile_clause
#         self.env.cr.execute(query, tuple(params))
# #         partner_ids = data['form'].get('custom_partner_ids', [])
#         partner_ids = docids
#         partners = obj_partner.browse(partner_ids)
#         partners = sorted(partners, key=lambda x: (x.ref, x.name))
#         docargs = {
#             'doc_ids': partner_ids,
#             'doc_model': self.env['res.partner'],
#             'data': data,
#             'docs': partners,
#             'time': time,
#             'lines': self._lines,
#             'sum_partner': self._sum_partner,
#         }
#         return docargs  # odoo11
