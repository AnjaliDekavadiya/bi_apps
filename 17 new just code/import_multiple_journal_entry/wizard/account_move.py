# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import io
import datetime
import tempfile
import binascii
import itertools
from datetime import date, datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _, exceptions
import logging
import xlrd


_logger = logging.getLogger(__name__)

# try:
#     import xlrd
#     try:
#         from xlrd import xlsx
#     except ImportError:
#         xlsx = None
# except ImportError:
#     _logger.debug('Cannot `import XL`.')

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class gen_journal_entry(models.TransientModel):
    _name = "gen.journal.entry"

    file_to_upload = fields.Binary('File')
    import_option = fields.Selection([('csv', 'CSV File'), ('xls', 'XLS File')], string='Select', default='csv')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)

    def find_account_id(self, account_code):
        if account_code:
            account_ids = self.env['account.account'].search([('code', 'in', account_code.split('.'))])
            if account_ids:
                account_id = account_ids[0]
                return account_id
            else:
                raise ValidationError(_('"%s" Wrong Account Code') % (account_code))

    def find_date(self, date):
        DATETIME_FORMAT = "%Y-%m-%d"
        if date:
            new_date = date.split(' ')
            try:
                p_date = datetime.strptime(new_date[0], DATETIME_FORMAT)
                return p_date
            except Exception:
                raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
        else:
            raise ValidationError(_('Please add Date field in sheet.'))

    def check_desc(self, name):
        if name:
            return name
        else:
            return '/'

    def find_partner(self, partner_name):
        partner_ids = self.env['res.partner'].search([('name', '=', partner_name)])
        if partner_ids:
            partner_id = partner_ids[0]
            return partner_id
        else:
            partner_id = None

    def check_currency(self, cur_name):
        currency_ids = self.env['res.currency'].search([('name', '=', cur_name)])
        if currency_ids:
            currency_id = currency_ids[0]
            return currency_id
        else:
            currency_id = None
            return currency_id

    
    def create_import_move_lines(self, values):
        move_line_obj = self.env['account.move.line']
        move_obj = self.env['account.move']
        if values.get('partner'):
            partner_name = values.get('partner')
            if self.find_partner(partner_name) != None:
                partner_id = self.find_partner(partner_name)
                values.update({'partner_id': partner_id.id})

        if values.get('currency'):
            cur_name = values.get('currency')
            if cur_name != '' and cur_name != None:
                currency_id = self.check_currency(cur_name)
                if currency_id != None:
                    values.update({'currency_id': currency_id.id})
                else:
                    raise ValidationError(_('"%s" Currency is not  in the system') % (cur_name))

        if values.get('name'):
            desc_name = values.get('name')
            name = self.check_desc(desc_name)
            values.update({'name': name})

        if values.get('date_maturity'):
            date = self.find_date(values.get('date_maturity'))
            values.update({'date_maturity': date})

        if values.get('date'):
            date = self.find_date(values.get('date'))



        if values.get('account_code'):
            account_code = values.get('account_code')
            account_id = self.find_account_id(str(account_code))
            if account_id != None:
                values.update({'account_id': account_id.id})
            else:
                raise ValidationError(_('"%s" Wrong Account Code') % (account_code))

        if values.get('debit') != '':
            values.update({'debit': float(values.get('debit'))})
            if float(values.get('debit')) < 0:
                values.update({'credit': abs(values.get('debit'))})
                values.update({'debit': 0.0})
        else:
            values.update({'debit': float('0.0')})

        if values.get('name') == '':
            values.update({'name': '/'})

        if values.get('credit') != '':
            values.update({'credit': float(values.get('credit'))})
            if float(values.get('credit')) < 0:
                values.update({'debit': abs(values.get('credit'))})
                values.update({'credit': 0.0})
        else:
            values.update({'credit': float('0.0')})

        if values.get('amount_currency') != '':
            values.update({'amount_currency': float(values.get('amount_currency'))})

       
        analytic_distribution_ids = []
        if values.get('analytic_distribution'):
            if ';' in  values.get('analytic_distribution'):
                analytic_distribution_names = values.get('analytic_distribution').split(';')
                for name in analytic_distribution_names:
                    distribution= self.env['account.analytic.account'].search([('name', '=', name)])
                    if not distribution:
                        raise ValidationError(_('"%s" Wrong Analytic Account') % (name))
                    analytic_distribution_ids.append(distribution.id)

            elif ',' in  values.get('analytic_distribution'):
                analytic_distribution_names = values.get('analytic_distribution').split(',')
                for name in analytic_distribution_names:
                    distribution= self.env['account.analytic.account'].search([('name', '=', name)])
                    if not distribution:
                        raise ValidationError(_('"%s" Wrong Analytic Account') % (name))
                    analytic_distribution_ids.append(distribution.id)
            else:
                analytic_distribution_names = values.get('analytic_distribution').split(',')
                for name in analytic_distribution_names:
                    distribution = self.env['account.analytic.account'].search([('name', '=', name)])
                    if not distribution:
                        raise ValidationError(_('"%s" Wrong Analytic Account') % (name))
                    analytic_distribution_ids.append(distribution.id)

        if analytic_distribution_ids:
            if len(analytic_distribution_ids) ==4 :
                analytic_distribution_dictionary = { distribution : 25 for distribution in analytic_distribution_ids }
            elif len(analytic_distribution_ids)== 3 :
                analytic_distribution_dictionary = { distribution : 33 for distribution in analytic_distribution_ids }
            elif len(analytic_distribution_ids)== 2 :
                analytic_distribution_dictionary = { distribution : 50 for distribution in analytic_distribution_ids }
            elif len(analytic_distribution_ids)== 1 :
                analytic_distribution_dictionary = { distribution : 100 for distribution in analytic_distribution_ids }

            values.update({'analytic_distribution' : analytic_distribution_dictionary})
    
        return values



    def import_move_lines(self):
        if self.import_option == 'csv':
            keys = ['date', 'ref', 'journal', 'name', 'partner', 'analytic_distribution', 'account_code', 'date_maturity',
                    'debit', 'credit', 'amount_currency', 'currency']
            try:
                csv_data = base64.b64decode(self.file_to_upload)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise ValidationError(_("Invalid file!"))

            values = {}
            lines = []
            data = []
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        data.append(values)

            data1 = {}
            sorted_data = sorted(data, key=lambda x: x['ref'])
            list1 = []
            for key, group in itertools.groupby(sorted_data, key=lambda x: x['ref']):
                small_list = []
                for i in group:
                    small_list.append(i)
                    data1.update({key: small_list})

            for key in data1.keys():
                lines = []
                values = data1.get(key)
                for val in values:
                    res = self.create_import_move_lines(val)
                    if not val.get('date') or not val.get('date_maturity'):
                        raise ValidationError(_('Define Date or Amount In Corresponding Columns !!!'))
                    move_obj = self.env['account.move']
                    if val.get('journal'):
                        journal_search = self.env['account.journal'].sudo().search(
                            [('name', '=', val.get('journal')), ('company_id', '=', self.company_id.id)])
                        if journal_search:
                            move1 = move_obj.search([('date', '=', val.get('date')),
                                                     ('ref', '=', val.get('ref')),
                                                     ('journal_id', '=', journal_search.name)])
                            if move1:
                                move = move1
                            else:
                                move = move_obj.create(
                                    {'date': val.get('date') or False, 'ref': val.get('ref') or False,
                                     'journal_id': journal_search.id})
                        else:    
                            raise ValidationError(_('Please Define Journal which are already in system.'))
                    else:
                        raise ValidationError(_('Please Define Journal In Corresponding Columns !!!.'))
                    del res['journal'], res['partner'], res['account_code'], res['currency']
                    lines.append((0, 0, res))
                move.write({'line_ids': lines})
        else:
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file_to_upload))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:

                raise exceptions.ValidationError(_('Invalid File!!'))
            product_obj = self.env['product.product']
            lines = []
            data = []
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(row_no)))

                    date = False
                    if line[7] != '' and line[0] != '':
                        if line[7].split('/'):
                            if len(line[7].split('/')) > 1:
                                raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                            if len(line[7]) > 8 or len(line[7]) < 5:
                                raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                        if line[0].split('/'):
                            if len(line[0].split('/')) > 1:
                                raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
                            if len(line[0]) > 8 or len(line[0]) < 5:
                                raise ValidationError(_('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))

                        date = str(xlrd.xldate.xldate_as_datetime(int(float(line[7])), workbook.datemode))
                        main_date = str(xlrd.xldate.xldate_as_datetime(int(float(line[0])), workbook.datemode))
                        values = {'date': main_date,
                                  'ref': line[1],
                                  'journal': line[2],
                                  'name': line[3],
                                  'partner': line[4],
                                  'analytic_distribution': line[5],
                                  'account_code': line[6],
                                  'date_maturity': date,
                                  'debit': line[8],
                                  'credit': line[9],
                                  'amount_currency': line[10],
                                  'currency': line[11],
                                  }
                        data.append(values)
                    else:
                        raise ValidationError(_('Define Date or Amount In Corresponding Columns !!!'))
            data1 = {}

            sorted_data = sorted(data, key=lambda x: x['ref'])
            list1 = []
            for key, group in itertools.groupby(sorted_data, key=lambda x: x['ref']):
                small_list = []
                for i in group:
                    small_list.append(i)
                    data1.update({key: small_list})

            for key in data1.keys():
                lines = []
                values = data1.get(key)
                for val in values:
                    res = self.create_import_move_lines(val)
                    move_obj = self.env['account.move']
                    if val.get('journal'):
                        journal_search = self.env['account.journal'].sudo().search(
                            [('name', '=', val.get('journal')), ('company_id', '=', self.company_id.id)])
                        if journal_search:
                            move1 = move_obj.search([('date', '=', val.get('date')),
                                                     ('ref', '=', val.get('ref')),
                                                     ('journal_id', '=', journal_search.name)])
                            if move1:
                                move = move1
                            else:
                                move = move_obj.create({
                                    'date': val.get('date') or False,
                                    'ref': val.get('ref') or False,
                                    'journal_id': journal_search.id,
                                })
                        else:
                            raise ValidationError(_('Please Define Journal which are already in system.'))
                    else:
                        raise ValidationError(_('Please Define Journal In Corresponding Columns !!!.'))
                    del res['journal'], res['partner'], res['account_code'], res['currency']
                    lines.append((0, 0, res))
                move.write({'line_ids': lines})
