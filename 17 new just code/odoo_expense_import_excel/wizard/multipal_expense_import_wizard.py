# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
import datetime

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ImportexpenseWizard(models.TransientModel):
    _name = "multiple.expense.import"
    _description = 'Multiple Expense Import'

    files = fields.Binary(
        string="Import Excel File",
        )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id.id,
    )

    method = fields.Selection(
    selection=[('Expense','Expense'),
                ('Expense_sheet','Expense Sheet'),
    ],
    string="Import",
    default='Expense',
    required=True,
    )

    # @api.multi
    def import_multiple_expense_with_excel(self):
        if self.method == 'Expense':
        
            try:
                workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
            except:
                raise ValidationError("Please select .xls/xlsx file.")
            sheet_name = workbook.sheet_names()
            sheet = workbook.sheet_by_name(sheet_name[0])
            print("=================sheet================",sheet.ncols)
            number_of_rows = sheet.nrows
            list_expense =[]
            vals = {}
            product=self.env['product.product']
            product_uom=self.env['uom.uom']
            taxes=self.env['account.tax']
            account=self.env['account.account']
            employee=self.env['hr.employee']
            currency=self.env['res.currency']
            analytic_account=self.env['account.analytic.account']
            row = 1
            while(row < number_of_rows):
                
                description = sheet.cell(row,0).value
                if not description:
                    raise ValidationError('expense name should not be empty at row %s in excel file .'%(row+1))


                product_id=sheet.cell(row,1).value
                if product_id:
                    productId=product.search([('default_code', '=', product_id)], limit=1)
                if not product_id:
                    raise ValidationError('product name should not be empty at row %s in excel file .'%(row+1))

                # bill_reference=sheet.cell(row,2).value

                # paid_by = sheet.cell(row,8).value
                paid_by = sheet.cell(row,6).value

                # date=sheet.cell(row,3).value
                date=sheet.cell(row,2).value

#                account_id=sheet.cell(row,4).value
                # account_name=sheet.cell(row,4).value
                account_name=sheet.cell(row,3).value
                if account_name:
#                    account_id = account.sudo().search([('code', '=', account_id)], limit=1)
                    account_id = account.sudo().search([('code', '=', int(account_name))], limit=1)

                # employee_id=sheet.cell(row,5).value
                employee_id=sheet.cell(row,4).value
                if employee_id:
                    employee_id = employee.search([('name', '=', employee_id)], limit=1)

                # currency_id=sheet.cell(row,6).value
                currency_id=sheet.cell(row,5).value
                if currency_id:
                    currencyId = currency.search([('name', '=', currency_id)], limit=1)

                # analytic_account_id=sheet.cell(row,7).value
                # if analytic_account_id:
                    # analytic_accountId = analytic_account.search([('name', '=', analytic_account_id)], limit=1)
                # if sheet.ncols == 11:
                #     price_unit = sheet.cell(row,9).value
                #     print('----------------price-------------',price_unit)
                #     quantity = sheet.cell(row,10).value

                vals = { 
                    'name': description,
                    'product_id':productId.id,
                    # 'reference':bill_reference,
                    'date': datetime.datetime.strptime(date ,'%d-%m-%Y').strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'account_id':account_id.id,  
                    'employee_id':employee_id.id,
                    'currency_id':currencyId.id,
                    # 'analytic_account_id':analytic_accountId.id,
                    'payment_mode':paid_by,

                }
                
                new_line = self.env['hr.expense'].new(vals)
                # new_line._onchange_product_id()
                # new_line._onchange_product_uom_id()

                # new_line._compute_from_product_id_company_id()
                # new_line._check_product_uom_category()
                
                line_vals_dict = self.env['hr.expense']._convert_to_write({
                    name: new_line[name] for name in new_line._cache
                })
                line_vals_dict['account_id'] = account_id.id
                # if sheet.ncols == 11:
                    # line_vals_dict.update({
                            # 'unit_amount':price_unit,
                            # 'total_amount_currency':price_unit,
                            # 'quantity':quantity,
                        # })

                expense_id =self.env['hr.expense'].create(line_vals_dict)

                row = row + 1
                list_expense.append(expense_id.id)
                if expense_id:
                    action = self.env.ref('hr_expense.hr_expense_actions_my_all').sudo().read()[0]

                    action['domain'] = [('id','in',list_expense)]
                    action['context']={}

            return action


        elif self.method == 'Expense_sheet':

            try:
                workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
            except:
                raise ValidationError("Please select .xls/xlsx file.")
            # workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
            sheet_name = workbook.sheet_names()
            sheet = workbook.sheet_by_name(sheet_name[0])
            number_of_rows = sheet.nrows
            list_expense =[]
            list_expense_sheet = []
            vals = {}
            excel_dict={}
            expense_dict={}
            product=self.env['product.product']
            product_uom=self.env['uom.uom']
            taxes=self.env['account.tax']
            account=self.env['account.account']
            employee=self.env['hr.employee']
            currency=self.env['res.currency']
            manager=self.env['res.users']
            analytic_account=self.env['account.analytic.account']
            # analytic_tags=self.env['account.analytic.tag']
            row = 1
            while(row < number_of_rows):

                Number = sheet.cell(row,0).value
                report_summary = sheet.cell(row,1).value
                if report_summary in expense_dict:
                    report_summary=expense_dict[report_summary]
                    list_expense_sheet.append(report_summary)
                if Number in expense_dict:
                    report_summary = expense_dict.get(Number)
                if report_summary:
                    expense_dict.update({Number:report_summary})
                    list_expense_sheet.append(report_summary)
                if not report_summary:
                    raise ValidationError('expense name should not be empty at row %s in excel file .'%(row+1))


                employee_id=sheet.cell(row,2).value
                if employee_id:
                    employee_id = employee.search([('name', '=', employee_id)], limit=1)
                


#                paid_by=sheet.cell(row,3).value

                user_id=sheet.cell(row,3).value
                if user_id:
                    managerId = manager.search([('name', '=', user_id)], limit=1)

                if Number in excel_dict:
                    expense_id=excel_dict[Number]
                    list_expense.append(expense_id.id)
                else:

                    expense_vals = { 
                        'name': report_summary,
                        'employee_id':employee_id.id,
#                        'payment_mode':paid_by,
                        'user_id':managerId.id,
                        'company_id':self.company_id.id,
                    }
                  
                    expense_id =self.env['hr.expense.sheet'].create(expense_vals)
                    excel_dict.update({Number:expense_id})
                    list_expense.append(expense_id.id)


                description = sheet.cell(row,4).value
                if not description:
                    raise ValidationError('expense name should not be empty at row %s in excel file .'%(row+1))

                # analytic_account_id=sheet.cell(row,5).value
                # if analytic_account_id:
                #     analytic_accountId = analytic_account.search([
                #         ('name', '=', analytic_account_id),
                #         ('company_id', '=', self.company_id.id)
                #     ],limit=1)

                # product_id=sheet.cell(row,6).value
                product_id=sheet.cell(row,5).value
                if product_id:
                    productId=product.search([('default_code', '=', product_id)], limit=1)
                if not product_id:
                    raise ValidationError('product name should not be empty at row %s in excel file .'%(row+1))
                               
                # bill_reference=sheet.cell(row,7).value

                # account_id=sheet.cell(row,8).value
                account_id=sheet.cell(row,6).value
                if account_id:
                    accountId = account.sudo().search([
                        ('code', '=', int(account_id)),
                        ('company_id', '=', self.company_id.id)
                ])

                # currency_id=sheet.cell(row,9).value
                currency_id=sheet.cell(row,7).value
                if currency_id:
                    currencyId = currency.search([('name', '=', currency_id)], limit=1)
                    
                # paid_by=sheet.cell(row,10).value
                paid_by=sheet.cell(row,8).value

                # if sheet.ncols == 13:
                #     price_unit = sheet.cell(row,11).value

                #     quantity = sheet.cell(row,12).value

                expence_vals_sheet = { 
                    'name': description,
                    # 'analytic_account_id':analytic_accountId.id,
                    'product_id':productId.id,
#                    'expense_id':expense_id.id,
                    'sheet_id':expense_id.id,
                    # 'reference':bill_reference,
                    'account_id':accountId.id,  
                    'currency_id':currencyId.id,
                    'payment_mode':paid_by,
                }

                new_line = self.env['hr.expense'].new(expence_vals_sheet)
                # new_line._onchange_product_id()
                # new_line._onchange_product_uom_id()

                # new_line._compute_from_product_id_company_id()
                # new_line._check_product_uom_category()
                
                line_vals_dict = self.env['hr.expense']._convert_to_write({
                    name: new_line[name] for name in new_line._cache
                })
                line_vals_dict['account_id'] = accountId.id
                # if sheet.ncols == 13:
                #     line_vals_dict.update({
                #         'unit_amount':price_unit,
                #         'quantity':quantity,
                #     })
                row = row + 1
                expense_sheet_id =self.env['hr.expense'].create(line_vals_dict)

                expense_id.write({'expense_line_ids' : [(4,expense_sheet_id.id)]})
                list_expense.append(expense_id.id)
                if expense_id:
                    action = self.env.ref('hr_expense.action_hr_expense_sheet_my_all').sudo().read()[0]
                    action['domain'] = [('id','in',list_expense)]
                    action['context']={}

            return action

       

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
