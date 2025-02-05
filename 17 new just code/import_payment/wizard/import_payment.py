# -*- coding: utf-8 -*-

import base64
import xlrd
import datetime

from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime

class ImportPaymentExcel(models.TransientModel):
    _name = 'payment.import.excel'
    _description ='Payment Import Excel'
    
    file_import = fields.Binary(
        string='Import Excel File'
    )
    posted_payment = fields.Boolean(
        string='Auto Validate?',
         default=True
    )
    
    # @api.multi
    def import_payment(self):
        account_payment_obj = self.env['account.payment']
        customer_obj = self.env['res.partner']
        payment_currency_obj = self.env['res.currency']
        account_journal_obj = self.env['account.journal']
        payment_method_obj = self.env['account.payment.method']

        try:
            workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.file_import))
        except:
            raise ValidationError("Please select .xls/xlsx file...")

        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        import_list = []
        row = 1
        while(row < number_of_rows):
            currency_id = payment_currency_obj.search([('name', '=', sheet.cell(row, 6).value)])
            partner_id = customer_obj.search([('custom_customer_code', '=', int(sheet.cell(row, 3).value))])
            journal_id = account_journal_obj.search([('name', '=', sheet.cell(row, 4).value)])
            payment_method_id = payment_method_obj.search([('name', '=', 'Manual'), ('payment_type', '=', sheet.cell(row, 0).value)])
            if not currency_id:
                raise ValidationError('Please enter valid currency on row no %s'%(row+1))
            if not partner_id:
                raise ValidationError('Please enter valid customer code on row no %s'%(row+1))
            if not journal_id:
                raise ValidationError('Please enter valid journal on row no %s'%(row+1))
            if not payment_method_id:
                raise ValidationError('Please enter valid payment method or payment type on row no %s'%(row+1))

            payment_type = sheet.cell(row, 0).value
            if not sheet.cell(row, 1).value:
                raise ValidationError('Please enter valid partner type on row no %s'%(row+1))
            partner_type = sheet.cell(row, 1).value
            amount = sheet.cell(row, 5).value
            date = sheet.cell(row, 2).value
            memo = sheet.cell(row, 7).value
            vals = {
                'payment_method_id' : payment_method_id.id,
                'payment_type' : payment_type,
                'partner_type' :partner_type,
                'partner_id' : int(sheet.cell(row, 3).value),
                'journal_id' : journal_id.id,
                'amount' : amount,
                'currency_id' : currency_id.id,
                # 'payment_date' : date,
                #'payment_date' : (datetime.strptime(date, '%m/%d/%Y')).strftime(DF),
                'date' : (datetime.strptime(date, '%m/%d/%Y')).strftime(DF),
                #'communication' : memo,
                'ref' : memo,
            }
            row += 1
            account_payment_id = account_payment_obj.create(vals)
            if self.posted_payment:
                account_payment_id.action_post()
            account_payment_id = account_payment_id.id
            import_list.insert(row-1, account_payment_id)


        return {
        'type': 'ir.actions.act_window',
        'name': 'Account Payments',
        'res_model': 'account.payment',
        #'res_id': account_payment_id,
        'domain': "[('id','in',[" + ','.join(map(str, import_list)) + "])]",
        'view_type': 'form',
        'view_mode': 'tree,form',
        'target' : account_payment_id,
        }
