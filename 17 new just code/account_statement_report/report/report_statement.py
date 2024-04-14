# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountStatementPDF(models.AbstractModel):
    _name = 'report.account_statement_report.report_statement_pdf'
    _description = "Account Statement PDF"

    @api.model
    def _get_report_values(self, docids, data=None):
        docids = data.get('account_ids', docids)
        if not docids:
            raise UserError(_("content is missing, this report cannot be printed."))

        docs = self.env['account.account'].browse(docids)
        return {
            'doc_ids': self.ids,
            'docs': docs,
            'from_date': data.get('from_date', False),
            'to_date': data.get('to_date', False)
        }


class AccountStatementXLS(models.AbstractModel):
    _name = 'report.account_statement_report.report_statement_xlsx'
    _description = "Account Statement XLS"

    try:
        _inherit = 'report.report_xlsx.abstract'
    except ImportError:
        _logger.debug('Cannot find report_xlsx module for version 11')

    def _get_workbook_formats(self, workbook):
        format1 = workbook.add_format({
            'font_size': 20,
            'bottom': True,
            'right': True,
            'left': True,
            'top': True,
            'align': 'center',
            'bold': True,
            'valign': 'vcenter'
        })
        format2 = workbook.add_format({
            'bottom': True,
            'top': True,
            'right': True,
            'left': True,
            'font_size': 10,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'color': 'grey'
        })
        format3 = workbook.add_format({
            'bottom': True,
            'top': True,
            'right': True,
            'left': True,
            'font_size': 10,
            'bold': False,
            'align': 'center',
            'valign': 'vcenter'
        })
        return format1, format2, format3

    def generate_xlsx_report(self, workbook, data, records):
        sheet = workbook.add_worksheet("Tax Analysis")
        format1, format2, format3 = self._get_workbook_formats(workbook)
        sheet.set_column(1, 1, 30)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)
        # ====================================================================
        sheet.merge_range(1, 2, 0, 3, "Account Statement", format1)
        row = 3
        types = {
            "asset_receivable": _("Receivable"),
            "asset_cash": _("Bank and Cash"),
            "asset_current": _("Current Assets"),
            "asset_non_current": _("Non-current Assets"),
            "asset_prepayments": _("Prepayments"),
            "asset_fixed": _("Fixed Assets"),
            "liability_payable": _("Payable"),
            "liability_credit_card": _("Credit Card"),
            "liability_current": _("Current Liabilities"),
            "liability_non_current": _("Non-current Liabilities"),
            "equity": _("Equity"),
            "equity_unaffected": _("Current Year Earnings"),
            "income": _("Income"),
            "income_other": _("Other Income"),
            "expense": _("Expenses"),
            "expense_depreciation": _("Depreciation"),
            "expense_direct_cost": _("Cost of Revenue"),
            "off_balance": _("Off-Balance Sheet")
        }
        for record in records:
            sheet.write(row, 0, _("Account:"), format2)
            sheet.write(row, 1, record.name, format3)
            sheet.write(row, 2, _("Code:"), format2)
            sheet.write(row, 3, record.code, format3)
            row += 1
            sheet.write(row, 0, _("Type:"), format2)
            sheet.write(row, 1, types.get(record.account_type), format3)
            row += 2
            sheet.write(row, 0, _("Date"), format2)
            sheet.write(row, 1, _("Description"), format2)
            sheet.write(row, 2, _("Debit"), format2)
            sheet.write(row, 3, _("Credit"), format2)
            sheet.write(row, 4, _("Balance"), format2)

            row += 2
            total_debit = 0.0
            total_credit = 0.0
            domain = [('account_id', '=', record.id)]
            if data.get('from_date') and data.get('to_date'):
                domain += [('date', '>=', data.get('from_date')), ('date', '<=', data.get('to_date'))]
            cumm_balance = 0.0
            for line in self.env['account.move.line'].search(domain, order='date'):
                cumm_balance += (line.debit - line.credit)
                sheet.write(row, 0, line.date, format3)
                sheet.write(row, 1, _(line.name), format3)
                sheet.write(row, 2, line.debit, format3)
                sheet.write(row, 3, line.credit, format3)
                sheet.write(row, 4, cumm_balance, format3)
                total_debit += line.debit
                total_credit += line.credit
                row += 1
            sheet.write(row, 1, _("Total"), format2)
            sheet.write(row, 2, total_debit, format2)
            sheet.write(row, 3, total_credit, format2)
            sheet.write(row, 4, total_debit - total_credit, format2)
            row += 5
