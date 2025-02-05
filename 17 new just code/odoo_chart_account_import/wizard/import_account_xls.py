# -*- coding: utf-8 -*-

import base64
import xlrd
import sys

from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api

class ImportChartAccount(models.TransientModel):
    _name = 'import.chart.account'
    _description = 'Import Chart Account'
    
    files = fields.Binary(
        'Select Excel File (.xls / .xlsx supported)',
    )
    
    #@api.multi
    def import_file(self):
        account_obj = self.env['account.account']
        # account_type_obj = self.env['account.account.type']
        tax_obj = self.env['account.tax']
        company_obj = self.env['res.company']
        account_tag_obj = self.env['account.account.tag']
        currency_obj = self.env['res.currency']

        try:
            workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file...")
            
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        aList = []
        row = 1
        while(row < number_of_rows):
        
            code = sheet.cell(row,0).value
            name = sheet.cell(row,1).value
            account_type = sheet.cell(row,2).value
            # user_type_id = account_type_obj.search([('name','=',sheet.cell(row,2).value)])
            tax = tax_obj.search([('name','=',sheet.cell(row,3).value)])
            tag = account_tag_obj.search([('name','=',sheet.cell(row,4).value)])
            company = company_obj.search([('name','=',sheet.cell(row,5).value)])
            currency = currency_obj.search([('name','=',sheet.cell(row,6).value)])
            reconcile = sheet.cell(row,7).value
            deprecate = sheet.cell(row,8).value
            
            if not code:
                raise UserError('Code should be not an empty')
            if not name:
                raise UserError('Name should be not an empty')
            if not account_type:
                raise ValidationError('%s Account Type is invalid at row number %s '%(sheet.cell(row,2).value,row+1))

            # if not user_type_id:
            #     raise UserError('Account User Type should be not an empty')
            # else:
            #     user_type_id = user_type_id.id
            if company:
                company = company.id
            else:
                raise UserError('Please Insert Valid Company')
            if tax:
                tax = tax.ids
            if tag:
                tag = tag.ids
            if currency:
                currency = currency.id
            row = row+1
            vals = {
                    'code':int(code),
                    'name':name,
                    'account_type':account_type,
                    # 'user_type_id':user_type_id,
                    'tax_ids':[(6,0,tax)],
                    'tag_ids':[(6,0,tag)],
                    'company_id':company,
                    'currency_id':currency,
                    'reconcile':reconcile,
                    'deprecated':deprecate,
                    }
            account_id = account_obj.create(vals)
            account_id = account_id.id
            aList.insert(row-1, account_id)
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Chart of Account',
            'res_model': 'account.account',
            'res_id': account_id,
            'domain': "[('id','in',[" + ','.join(map(str, aList)) + "])]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target' : account_id,
        }
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
