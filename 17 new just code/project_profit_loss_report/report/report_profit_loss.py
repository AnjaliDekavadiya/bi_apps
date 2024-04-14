# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError, AccessError
import itertools
from operator import itemgetter



class ProjectProfitLossReport(models.AbstractModel):
    _name = 'report.project_profit_loss_report.profit_loss_report_probc'

    @api.model
    def _get_report_values(self, docids, data=None):
        Analytic = self.env['account.analytic.account']
        account_ids = []
        user_id = self.env.user
        if data.get('analytic_account_ids', []):
            analytic_account = data.get('analytic_account_ids', [])
            account_ids = Analytic.browse(analytic_account)
        data_dict = {}
        for account_id in account_ids:
            if data:
                account_line_ids = self.env['account.analytic.line'].search([
                    ('account_id', '=', account_id.id),
                    ('date', '>=', data.get('start_date', False)),
                    ('date', '<=', data.get('end_date', False))
                ])
            else:
                account_line_ids = self.env['account.analytic.line'].search(
                    [('account_id', '=', account_id.id)]
                )

            minus_amount = 0.0 
            plus_amount = 0.0 
            account_types = []
            types = []
            if account_id not in data_dict:
                data_dict[account_id] = {}
            for account_line_id in account_line_ids:
                if account_line_id.amount <= -1:
                    minus_amount += account_line_id.amount
                    bank_book = 'Expense'
                else:
                    plus_amount += account_line_id.amount
                    bank_book = 'Income'
                user_type = account_line_id.general_account_id.name
                single_amount = account_line_id.amount
                user_type_id = account_line_id.general_account_id.id
                has_dict = True
                for dict_id in account_types:
                    if dict_id['id'] == user_type_id:
                        dict_id['single_amount'] += single_amount
                        has_dict = False
                if has_dict:
                    account_types.append({
                        'user_type': user_type,
                        'single_amount': single_amount,
                        'bank_book': bank_book,
                        'id': user_type_id,
                    })


            account_types = sorted(account_types, key=itemgetter('bank_book'))
            for key, value in itertools.groupby(account_types, key=itemgetter('bank_book')):
                data_group  = []
                for i in value:
                    data_group.append(i)
                types.append(data_group)
            total = sum([minus_amount,plus_amount])
            data_dict[account_id] = {
                'minus_amount': minus_amount,
                'plus_amount': plus_amount,
                'account_types': types,
                'total': total,
            }
        report = self.env['ir.actions.report']._get_report_from_name(
            'project_profit_loss_report.profit_loss_report_probc'
        )
        return {
            'doc_ids': account_ids,
            'data': data,
            'doc_model': 'account.analytic.account',
            'docs': account_ids,
            'lines': data_dict,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: