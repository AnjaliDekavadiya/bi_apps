# -*- coding:utf-8 -*-

import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ImportInvoiceWizard(models.TransientModel):
    _name = 'import.invoice.wizard'
    _description = 'Import Invoice Wizard'
    
    import_type = fields.Selection(
        [('customer_invoice','Customer Invoice'),
         ('vendor_bill','Vendor Bill'),
         ('credit_note','Credit Note'),
         ('debit_note','Debit Note')],
        string='Type',
        default='customer_invoice',
    )
    import_product_by = fields.Selection(
        [('name','Name'),
         ('code','Code'),
         ('barcode','Barcode')],
        string='Import Product By',
        default='code',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        string='Company',
        default=lambda self: self.env.user.company_id.id
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Account Journal',
        required=True,
    )
    invoice_stage_option = fields.Selection(
        [('draft','Import Draft Invoice'),
         ('validate','Validate Invoice Automatically with Import')],
        string='Invoice Stage Option',
        default='draft',
    )
    account_option = fields.Selection(
        [('product_incexp_account','Use Account from Configuration Product/Property'),
         ('from_excel_account','Use Account from Excel')],
        string='Account Option',
        default='product_incexp_account',
    )#Remove 'Use Account from Excel' option due to remove account from excel becuase of odoo replace account from invoice line
    files = fields.Binary(string="Import Excel File")
    datas_fname = fields.Char('Select Excel File')

    def import_file(self):
        category_obj = self.env['product.category']
        tax_obj = self.env['account.tax']
        product_uom_obj = self.env['uom.uom']
        product_obj = self.env['product.product']
        partner_obj = self.env['res.partner']
        account_obj = self.env['account.analytic.account']
        # analytictag_obj = self.env['account.analytic.tag']
        invoice_line_obj = self.env['account.move.line']
        invoice_obj = self.env['account.move']
        product_account = self.env['account.account']

        if not self.import_product_by:
            raise ValidationError("Please select import product by.")
        
        try:
            workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        row = 1
        invoice_dict = {}
        account = False
        invoice_lists = []
        while(row < number_of_rows):
            account_id = account_obj.search([('name', '=', sheet.cell(row,9).value),('company_id','=',self.company_id.id)], limit=1)
            anlytic_tag_list = []
            tax_list = []
            analytictag_id = False
            # if sheet.cell(row,10).value:
            #     analytictag_names = sheet.cell(row,10).value.split(',')
            #     for tag_name in analytictag_names:
            #         analytictag_id = analytictag_obj.search([
            #             ('name', '=', tag_name),
            #         ],limit=1)
            #         if analytictag_id:
            #             anlytic_tag_list.append(analytictag_id.id)

            partner_id = partner_obj.search([('name','=', sheet.cell(row,1).value)], limit=1)

            if not partner_id:
                raise ValidationError(_(
                    "Partner not found for %s" %(sheet.cell(row,1).value)
                ))

            lang_code = self.env.context.get('lang') or 'en_US'
            lang = self.env['res.lang']
            lang_id = lang._lang_get(lang_code)
            date_format = lang_id.date_format

            invoice_date = sheet.cell(row,2).value
            invoice_date = datetime.strptime(invoice_date, '%d-%m-%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)

            product_id = False
            if self.import_product_by == 'name':
                product_id = product_obj.search([('name', '=', sheet.cell(row,3).value)], limit=1)
            elif self.import_product_by == 'code':
                product_id = product_obj.search([('default_code', '=', sheet.cell(row,3).value)], limit=1)
            elif self.import_product_by == 'barcode':
                product_id = product_obj.search([('barcode', '=', sheet.cell(row,3).value)], limit=1)
            if not product_id:
                raise ValidationError('%s product should not be empty at row number %s '%(sheet.cell(row,0).value,row+1))

            tax_type = ['none']
            if self.import_type in ['vendor_bill', 'debit_note']:
                tax_type.append('purchase')
            else:
                tax_type.append('sale')

            if sheet.cell(row,8).value:
                tax_names = sheet.cell(row,8).value.split(',')
                for tx_name in tax_names:
                    tax_id1 = tax_obj.search([
                        ('name', '=', tx_name),
                        ('company_id','=',self.company_id.id),
                        ('type_tax_use', 'in', tax_type)
                    ])
                    if tax_id1:
                        tax_list.append(tax_id1.id)

            comment = sheet.cell(row,11).value #Remove Account column from excel so it's decrease column from excel
            invoice_comments = ''
            inv_comment = ''

            excel_invoice = sheet.cell(row,0).value
            company_id = self.company_id.id
            p = partner_id if not company_id else partner_id.with_context(company_id=company_id).with_company(self.company_id) # 17/03/2021

            move_type = self.import_type
            if p:
                rec_account = p.property_account_receivable_id
                pay_account = p.property_account_payable_id
                if not rec_account and not pay_account:
                    action = self.env.ref('account.action_account_config')
                    msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                    raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

                if move_type in ('vendor_bill', 'debit_note'):
                    inv_account_id = pay_account.id
                    payment_term_id = p.property_supplier_payment_term_id.id
                else:
                    inv_account_id = rec_account.id
                    payment_term_id = p.property_payment_term_id.id

            if not excel_invoice:
                raise ValidationError("%s Please enter invoice id at row number at %s"%(sheet.cell(row,0).value, row+1))
            
            if not self.import_type:
                raise ValidationError("Please select import type.")

            if not excel_invoice in invoice_dict:
                invoice_vals = {
                    'partner_id': partner_id.id, 
                    'invoice_date': invoice_date,
                    'journal_id' : self.journal_id.id,
                    'company_id' : self.company_id.id,
                    'invoice_payment_term_id': payment_term_id,
                    'invoice_line_ids': [],
                    'narration': ''
                }
                invoice_dict.update({excel_invoice: invoice_vals})
                invoice_lists.append(excel_invoice)
            else:
                invoice_vals = invoice_dict.get(excel_invoice)

            if self.import_type == 'credit_note':
                invoice_vals.update({'move_type': 'out_refund'})
            elif self.import_type == 'debit_note':
                invoice_vals.update({'move_type': 'in_refund'})
            elif self.import_type == 'customer_invoice':
                invoice_vals.update({'move_type': 'out_invoice'})
            elif self.import_type == 'vendor_bill':
                invoice_vals.update({'move_type': 'in_invoice'})

            if invoice_vals.get('move_type') in ['out_invoice', 'in_refund']:
                if self.account_option == 'product_incexp_account':
                    account = product_id.property_account_income_id or product_id.categ_id.property_account_income_categ_id
                else:
                    account = product_account.search([('code','=', code),('company_id','=',self.company_id.id)], limit=1)

            if invoice_vals.get('move_type') in ['in_invoice', 'out_refund']:
                if self.account_option == 'product_incexp_account':
                    account = product_id.property_account_expense_id or product_id.categ_id.property_account_expense_categ_id
                else:
                    account = product_account.search([('code','=', code),('company_id','=',self.company_id.id)], limit=1)

            if not account and self.account_option == 'product_incexp_account':
                raise ValidationError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') % \
                    (product_id.name, product_id.id, product_id.categ_id.name))
            elif not account:
                raise ValidationError(_('Please define account for this code: "%s" ') % (code))

            if not sheet.cell(row,5).value:
                raise ValidationError('%s Product quantity should be empty at row number %s '%(sheet.cell(row,5).value,row+1))
            if not sheet.cell(row,6).value:
                raise ValidationError('%s Product price unit should be empty at row number %s '%(sheet.cell(row,6).value,row+1))

            
            invoice_line_dict = {
                'name': sheet.cell(row,4).value,
                'product_id': product_id.id,
                'quantity': sheet.cell(row,5).value,
                'discount': sheet.cell(row,7).value,
                'price_unit': sheet.cell(row,6).value,
                'tax_ids': [(6, 0, tax_list)],
                # 'analytic_tag_ids': [(6, 0, anlytic_tag_list)],
                # 'analytic_account_id': account_id.id,
            }
            invoice_vals.get('invoice_line_ids').append((0, 0, invoice_line_dict))
            if invoice_vals.get('narration') == '':
                invoice_vals['narration'] = comment
            else:
                invoice_vals['narration'] = invoice_vals.get('narration') + ', ' + comment
            row = row+1

        created_moves = self.env['account.move']
        for invoice in invoice_lists:
            moves = self.env['account.move'].sudo().create(invoice_dict.get(invoice))
            if self.invoice_stage_option == 'validate':
                moves.action_post()
            created_moves += moves

        if self.import_type == 'customer_invoice':
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        elif self.import_type == 'vendor_bill':
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        elif self.import_type == 'credit_note':
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_refund_type")
        elif self.import_type == 'debit_note':
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_refund_type")
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action['domain'] = [('id', 'in', created_moves.ids)]
        return action

#     #@api.multi
#     def import_file(self):
#         category_obj = self.env['product.category']
#         tax_obj = self.env['account.tax']
#         product_uom_obj = self.env['uom.uom']
#         product_obj = self.env['product.product']
#         partner_obj = self.env['res.partner']
#         account_obj = self.env['account.analytic.account']
#         analytictag_obj = self.env['account.analytic.tag']
# #        invoice_line_obj = self.env['account.invoice.line']
# #        invoice_obj = self.env['account.invoice']
#         invoice_line_obj = self.env['account.move.line']
#         invoice_obj = self.env['account.move']
#         product_account = self.env['account.account']
        
#         if not self.import_product_by:
#             raise ValidationError("Please select import product by.")
        
#         try:
#             workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
#         except:
#             raise ValidationError("Please select .xls/xlsx file...")
#         Sheet_name = workbook.sheet_names()
#         sheet = workbook.sheet_by_name(Sheet_name[0])
#         number_of_rows = sheet.nrows
#         row = 1
#         invoice_dict = {}
#         account = False
#         invoice_lists = []
#         while(row < number_of_rows):
#             account_id = account_obj.search([('code', '=', sheet.cell(row,13).value),('company_id','=',self.company_id.id)], limit=1)
#             if not account_id:
#                 account_id = account_obj.search([('name', '=', sheet.cell(row,9).value),('company_id','=',self.company_id.id)], limit=1)
#             anlytic_tag_list = []
#             tax_list = []
#             analytictag_id = False
#             if sheet.cell(row,10).value:
#                 analytictag_names = sheet.cell(row,10).value.split(',')
#                 for tag_name in analytictag_names:
#                     analytictag_id = analytictag_obj.search([
#                         ('name', '=', tag_name),
#                         # ('company_id','=',self.company_id.id)
#                     ],limit=1)
#                     if analytictag_id:
#                         anlytic_tag_list.append(analytictag_id.id)

#             partner_id = partner_obj.search([('ref','=', sheet.cell(row,12).value)], limit=1)
#             if not partner_id:
#                 partner_id = partner_obj.search([('name','=', sheet.cell(row,1).value)], limit=1)

#             # partner_id = partner_obj.search([('name','=', sheet.cell(row,1).value)], limit=1)
#             if not partner_id:
#                 raise ValidationError(_(
#                     "Partner not found for %s" %(sheet.cell(row,1).value)
#                 ))

#             lang_code = self.env.context.get('lang') or 'en_US'
#             lang = self.env['res.lang']
#             lang_id = lang._lang_get(lang_code)
#             date_format = lang_id.date_format

#             invoice_date = sheet.cell(row,2).value
#             invoice_date = datetime.strptime(invoice_date, '%d-%m-%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)

#             product_id = False
#             if self.import_product_by == 'name':
#                 product_id = product_obj.search([('name', '=', sheet.cell(row,3).value)], limit=1)
#             elif self.import_product_by == 'code':
#                 product_id = product_obj.search([('default_code', '=', sheet.cell(row,3).value)], limit=1)
#             elif self.import_product_by == 'barcode':
#                 product_id = product_obj.search([('barcode', '=', sheet.cell(row,3).value)], limit=1)
#             if not product_id:
#                 raise ValidationError('%s product should not be empty at row number %s '%(sheet.cell(row,0).value,row+1))

#             tax_type = ['none']
#             if self.import_type in ['vendor_bill', 'debit_note']:
#                 tax_type.append('purchase')
#             else:
#                 tax_type.append('sale')

#             if sheet.cell(row,8).value:
#                 tax_names = sheet.cell(row,8).value.split(',')
#                 for tx_name in tax_names:
#                     tax_id1 = tax_obj.search([
#                         ('name', '=', tx_name),
#                         ('company_id','=',self.company_id.id),
#                         ('type_tax_use', 'in', tax_type)
#                     ])
#                     if tax_id1:
#                         tax_list.append(tax_id1.id)

# #            comment = sheet.cell(row,12).value
#             comment = sheet.cell(row,11).value #Remove Account column from excel so it's decrease column from excel
#             invoice_comments = ''
#             inv_comment = ''
            
#             excel_invoice = sheet.cell(row,0).value
            
#             company_id = self.company_id.id
#             # company_x = self.env['res.company'].browse(company_id) # 17/03/2021
#             # p = partner_id if not company_id else partner_id.with_context(force_company=company_id) # 17/03/2021 
#             p = partner_id if not company_id else partner_id.with_context(company_id=company_id).with_company(self.company_id) # 17/03/2021 
#             # type = self.import_type
#             move_type = self.import_type
#             if p:
#                 rec_account = p.property_account_receivable_id
#                 pay_account = p.property_account_payable_id
#                 if not rec_account and not pay_account:
#                     action = self.env.ref('account.action_account_config')
#                     msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
#                     raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
    
#                 # if type in ('vendor_bill', 'debit_note'):
#                 if move_type in ('vendor_bill', 'debit_note'):
#                     inv_account_id = pay_account.id
#                     payment_term_id = p.property_supplier_payment_term_id.id
#                 else:
#                     inv_account_id = rec_account.id
#                     payment_term_id = p.property_payment_term_id.id
            
#             if not excel_invoice:
#                 raise ValidationError("%s Please enter invoice id at row number at %s"%(sheet.cell(row,0).value, row+1))
            
#             if not self.import_type:
#                 raise ValidationError("Please select import type.")
        
#             if not excel_invoice in invoice_dict:
#                 if self.import_type == 'credit_note':
#                     invoice_id = invoice_obj.create({
#                                                      'partner_id': partner_id.id, 
#                                                      # 'type': 'out_refund',
#                                                      'move_type': 'out_refund',
#                                                      #'date_invoice': invoice_date,
#                                                      'invoice_date': invoice_date,
#                                                      'journal_id' : self.journal_id.id,
#                                                      'company_id' : self.company_id.id,
#                                                      #'payment_term_id': payment_term_id,
#                                                      'invoice_payment_term_id': payment_term_id,
#                                                      #'account_id' : inv_account_id
#                                                      })
#                     invoice_id._onchange_partner_id() 
                    
                    
#                 elif self.import_type == 'debit_note':
#                     invoice_id = invoice_obj.create({
#                                                      'partner_id': partner_id.id, 
#                                                      # 'type': 'in_refund',
#                                                      'move_type': 'in_refund',
#                                                      #'date_invoice': invoice_date,
#                                                      'invoice_date': invoice_date,
#                                                      'journal_id' : self.journal_id.id,
#                                                      'company_id' : self.company_id.id,
#                                                      #'payment_term_id': payment_term_id,
#                                                      'invoice_payment_term_id': payment_term_id,
#                                                      #'account_id' : inv_account_id
#                                                      })
#                     invoice_id._onchange_partner_id()
                    
#                 elif self.import_type == 'customer_invoice':
#                     invoice_id = invoice_obj.create({
#                                                      'partner_id': partner_id.id, 
#                                                      # 'type': 'out_invoice',
#                                                      'move_type': 'out_invoice',
#                                                      #'date_invoice': invoice_date,
#                                                      'invoice_date': invoice_date,
#                                                      'journal_id' : self.journal_id.id,
#                                                      'company_id' : self.company_id.id,
#                                                      #'payment_term_id': payment_term_id,
#                                                      'invoice_payment_term_id': payment_term_id,
#                                                      #'account_id' : inv_account_id
#                                                      })
#                     invoice_id._onchange_partner_id()
                    
#                 elif self.import_type == 'vendor_bill':
#                     invoice_id = invoice_obj.create({
#                                                      'partner_id': partner_id.id, 
#                                                      # 'type': 'in_invoice',
#                                                      'move_type': 'in_invoice',
#                                                      #'date_invoice': invoice_date,
#                                                      'invoice_date': invoice_date,
#                                                      'journal_id' : self.journal_id.id,
#                                                      'company_id' : self.company_id.id,
#                                                      #'payment_term_id': payment_term_id,
#                                                      'invoice_payment_term_id': payment_term_id,
#                                                      #'account_id' : inv_account_id
#                                                      })
#                     invoice_id._onchange_partner_id()
#                 invoice_dict.update({excel_invoice :invoice_id})
#             else:
#                 invoice_id = invoice_dict.get(excel_invoice)
                
# #            code = sheet.cell(row,11).value

#             # if invoice_id.type == 'out_invoice':
#             if invoice_id.move_type == 'out_invoice':
#                 if self.account_option == 'product_incexp_account':
#                     account = product_id.property_account_income_id or product_id.categ_id.property_account_income_categ_id
#                 else:
#                     account = product_account.search([('code','=', code),('company_id','=',self.company_id.id)], limit=1)
                    
#             # if invoice_id.type == 'in_invoice':
#             if invoice_id.move_type == 'in_invoice':
#                 if self.account_option == 'product_incexp_account':
#                     account = product_id.property_account_expense_id or product_id.categ_id.property_account_expense_categ_id
#                 else:
#                     account = product_account.search([('code','=', code),('company_id','=',self.company_id.id)], limit=1)
            
#             # if invoice_id.type == 'in_refund':
#             if invoice_id.move_type == 'in_refund':
#                 if self.account_option == 'product_incexp_account':
#                     account = product_id.property_account_income_id or product_id.categ_id.property_account_income_categ_id
#                 else:
#                     account = product_account.search([('code','=', code),('company_id','=',self.company_id.id)], limit=1)
                    
#             # if invoice_id.type == 'out_refund':
#             if invoice_id.move_type == 'out_refund':
#                 if self.account_option == 'product_incexp_account':
#                     account = product_id.property_account_expense_id or product_id.categ_id.property_account_expense_categ_id
#                 else:
#                     account = product_account.search([('code','=', code),('company_id','=',self.company_id.id)], limit=1)
            
#             #if self.account_option == 'product_incexp_account':
#             #    account = product_id.property_account_expense_id or product_id.categ_id.property_account_expense_categ_id
#             #else:
#             #    account = product_account.search([('code','=',code),('company_id','=',self.company_id.id)], limit=1)
#             if not account and self.account_option == 'product_incexp_account':
#                 raise ValidationError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') % \
#                     (product_id.name, product_id.id, product_id.categ_id.name))
#             elif not account:
#                 raise ValidationError(_('Please define account for this code: "%s" ') % (code))
# #             uom_name = sheet.cell(row,6).value
# #             uom_id = product_uom_obj.search([('name', '=', str(uom_name))])
            
#             if not sheet.cell(row,5).value:
#                 raise ValidationError('%s Product quantity should be empty at row number %s '%(sheet.cell(row,5).value,row+1))
#             if not sheet.cell(row,6).value:
#                 raise ValidationError('%s Product price unit should be empty at row number %s '%(sheet.cell(row,6).value,row+1))
            
#             if invoice_id:
#                 vals = {
# #                    'account_id' : account.id, REMOVE FROM V13 Due to replace account from odoo logic
# #                    'account_analytic_id' : account_id.id,
#                     'analytic_account_id' : account_id.id,
#                     'analytic_tag_ids' : [(6, 0, anlytic_tag_list)],
#                     'product_id' : product_id.id,
#                     'name' : sheet.cell(row,4).value,
#                     'price_unit' : sheet.cell(row,6).value,
#                     #'uom_id' : uom_id.id,
#                     'discount' : sheet.cell(row,7).value,
# #                    'invoice_line_tax_ids': [(6, 0, tax_list)],
#                     'tax_ids': [(6, 0, tax_list)],
# #                    'invoice_id': invoice_id.id,
#                     'move_id': invoice_id.id,
#                     }

#                 inv_line_new = invoice_line_obj.new(vals)
#                 inv_line_new._onchange_product_id()
#                 inv_line_new._onchange_account_id()
#                 inv_line_new._onchange_uom_id()
#                 inv_line_values = inv_line_new._convert_to_write({
#                    name: inv_line_new[name] for name in inv_line_new._cache
#                 })
#                 inv_line_values.update({
#                     'price_unit': sheet.cell(row,6).value,
#                     'name' : sheet.cell(row,4).value,
# #                    'invoice_line_tax_ids': [(6, 0, tax_list)],
#                     'tax_ids': [(6, 0, tax_list)],
# #                    'account_id' : account.id, REMOVE FROM V13 Due to replace account from odoo logic
#                     'quantity': sheet.cell(row,5).value
#                 })
#                 invoice_id.with_context({'special_custom_invoice_import':True}).write({
#                     'invoice_line_ids' : [(0, 0, inv_line_values)]
#                 })
# #                invoice_line = invoice_line_obj.create(inv_line_values)
                
# #                if invoice_id.comment:
# #                    inv_comment = invoice_id.comment+','
#                 if invoice_id.narration:
#                     inv_comment = invoice_id.narration+','
#                 invoice_comments = str(inv_comment) + comment
#                 row = row+1
                
# #                invoice_id.write({'comment' : invoice_comments })
#                 invoice_id.write({'narration' : invoice_comments })
#             invoice_id._onchange_invoice_line_ids()
#             if self.invoice_stage_option == 'validate':
#                 for invoice in invoice_dict:
#                     #invoice_id.action_invoice_open()
#                     invoice_id.action_post()
                    
                    
#             invoice_lists.append(invoice_id.id) 
        
#         if self.import_type == 'customer_invoice':
# #            result = self.env.ref('account.action_invoice_tree1')
#             result = self.env.ref('account.action_move_out_invoice_type')
#             action_ref = result or False
#             action = action_ref.sudo().read()[0]
#             action['domain'] = [('id', 'in', invoice_lists)]
            
#         if self.import_type == 'vendor_bill':
#             #result = self.env.ref('account.action_vendor_bill_template')
#             result = self.env.ref('account.action_move_in_invoice_type')
#             action_ref = result or False
#             action = action_ref.sudo().read()[0]
#             action['domain'] = [('id', 'in', invoice_lists)]
        
#         if self.import_type == 'credit_note':
#             #result = self.env.ref('account.action_invoice_out_refund')
#             result = self.env.ref('account.action_move_out_refund_type')
#             action_ref = result or False
#             action = action_ref.sudo().read()[0]
#             action['domain'] = [('id', 'in', invoice_lists)]
            
#         if self.import_type == 'debit_note':
#             #result = self.env.ref('account.action_invoice_in_refund')
#             result = self.env.ref('account.action_move_in_refund_type')
#             action_ref = result or False
#             action = action_ref.sudo().read()[0]
#             action['domain'] = [('id', 'in', invoice_lists)]
        
#         return action
           
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
