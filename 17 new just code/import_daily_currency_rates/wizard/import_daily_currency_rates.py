# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import base64
import xlrd

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError


class CurrencyDailyRates(models.TransientModel):
    _name = "currency.rates.import"
    _description = 'Currency Daily Rates'

    files = fields.Binary(
        string="Select Excel File",
        )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
        )

    # @api.multi #odoo13
    def import_currency_rates(self):
        """This method is used to the import the currency
        rate using excel file."""
        try:
            workbook = xlrd.open_workbook(
                file_contents=base64.decodebytes(self.files)
            )
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        currency_rates = []
        currency_id = self.env['res.currency']
        sheet_number = sheet.row_values(0)
        currency_name = sheet_number.index('Currency Name')
        currency_date = sheet_number.index('Date')
        currency_rate = sheet_number.index('Rate')
        row = 1
        while row < number_of_rows:
            currency = sheet.cell(row, currency_name).value
            if not currency:
                raise ValidationError(
                    "Currency Name is not found at row number %s."
                    % (row+1)
                )
            if currency:
                currency_id = currency_id.search(
                    [('name', '=', currency)], limit=1)
                if not currency_id:
                    raise ValidationError(
                        '%s this Currency Name is not found.' % (currency))
            date = sheet.cell(row, currency_date).value
            date = datetime.strptime(date, '%m/%d/%Y')
            if not date:
                raise ValidationError(
                    "Date is not found at row number %s."
                    % (row+1)
                )
            rate = sheet.cell(row, currency_rate).value
            if not rate:
                raise ValidationError(
                    "Rate is not found at row number %s."
                    % (row+1)
                )
            vals = {
                'currency_id': currency_id.id,
                'name': date.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'rate': rate,
                'company_id': self.company_id.id,
            }
            row = row + 1
            rate_id = self.env['res.currency.rate'].create(vals)
            currency_rates.append(rate_id.id)
            if rate_id:
                action = self.env.ref('base.act_view_currency_rates').sudo().read()[0]

                action['domain'] = [('id', 'in', currency_rates)]
                action['context'] = {}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
