# -*- coding:utf-8 -*-

import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class InvoiceImportWizard(models.TransientModel):
    _name = 'invoice.import.wizard'

    files = fields.Binary(string="Import Excel File")
    datas_fname = fields.Char('Import File Name')

    #@api.multi
    def import_file(self):
        active_id = self._context.get('active_id')
        category_obj = self.env['product.category']
        tax_obj = self.env['account.tax']
        product_uom_obj = self.env['uom.uom']
        product_obj = self.env['product.product']
        account_obj = self.env['account.analytic.account']
        # analytictag_obj = self.env['account.analytic.tag']
#        invoice_line_obj = self.env['account.invoice.line']
#        invoice_obj = self.env['account.invoice'].browse(active_id)
        invoice_obj = self.env['account.move'].browse(active_id)
        #try:
        #    workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        #except:
        #    raise ValidationError("Please select .xls/xlsx file...")
        #workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        row = 1
        while(row < number_of_rows):
            tlist = []
            product_id = product_obj.search([('name', '=', sheet.cell(row,0).value)], limit=1)
            if not product_id:
                raise ValidationError(_("%s Product is not found." %(sheet.cell(row,0).value)))

            if not sheet.cell(row,2).value:
                raise ValidationError('%s Product quantity should be empty at row number %s '%(sheet.cell(row,2).value,row+1))

            uom_id = product_uom_obj.search([('name', '=', sheet.cell(row,3).value)])
            if sheet.cell(row,3).value and not uom_id:
                raise ValidationError(_("%s unit of measure is not found." %(sheet.cell(row,3).value)))
            if not uom_id and product_id:
                uom_id = product_id.uom_id

            if not sheet.cell(row,4).value:
                raise ValidationError('%s Product price unit should be empty at row number %s '%(sheet.cell(row,4).value,row+1))

            tax_id1 = tax_obj.search([('name', '=', sheet.cell(row,6).value)])
            tax_id2 = tax_obj.search([('name', '=', sheet.cell(row,7).value)])
            tax_id3 = tax_obj.search([('name', '=', sheet.cell(row,8).value)])
            if sheet.cell(row,6).value and not tax_id1:
                raise ValidationError(_("%s Tax is not found." %(sheet.cell(row,6).value)))
            if sheet.cell(row,7).value and not tax_id2:
                raise ValidationError(_("%s Tax is not found." %(sheet.cell(row,7).value)))
            if sheet.cell(row,8).value and not tax_id3:
                raise ValidationError(_("%s Tax is not found." %(sheet.cell(row,8).value)))

            account_id = account_obj.search([('name', '=', sheet.cell(row,9).value)])
            if sheet.cell(row,9).value and not account_id:
                raise ValidationError(_("%s analytic account is not found." %(sheet.cell(row,9).value)))

            if not tax_id1 and not tax_id2 and not tax_id3:
                if product_id.taxes_id:
                    if invoice_obj.move_type == 'out_invoice':
                        tlist += product_id.taxes_id.ids
                    if invoice_obj.move_type == 'in_invoice':
                        tlist += product_id.supplier_taxes_id.ids

            anlytic_tag_list = []
            account = False
            analytictag_list = list((sheet.cell(row,10).value).split(","))
            # analytictag_ids = analytictag_obj.search([('name', 'in', analytictag_list)])
            # if analytictag_ids:
            #     anlytic_tag_list = analytictag_ids.ids
            
#            if invoice_obj.type == 'out_invoice' and product_id:
#                account = product_id.property_account_income_id or product_id.categ_id.property_account_income_categ_id
#            if invoice_obj.type == 'in_invoice' and product_id:
#                account = product_id.property_account_expense_id or product_id.categ_id.property_account_expense_categ_id

            fiscal_position = invoice_obj.fiscal_position_id
            accounts = product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
            if invoice_obj.is_sale_document(include_receipts=True):
                # Out invoice.
                account = accounts['income']
            elif invoice_obj.is_purchase_document(include_receipts=True):
                # In invoice.
                account = accounts['expense']

            if not account:
                raise ValidationError(_('Please define income/expense account for this product: "%s" (id:%d) - or for its category: "%s".') % \
                    (product_id.name, product_id.id, product_id.categ_id.name))
            if tax_id1:
                tlist.append(tax_id1.id)
            if tax_id2:
                tlist.append(tax_id2.id)
            if tax_id3:
                tlist.append(tax_id3.id)

            if not product_id:
                raise ValidationError('%s product should be empty at row number %s '%(sheet.cell(row,0).value,row+1))
            #account = product_id.property_account_expense_id or product_id.categ_id.property_account_expense_categ_id
            
            vals = {
                'account_id' : account.id,
#                'account_analytic_id' : account_id.id,
                # 'analytic_account_id' : account_id.id,
                # 'analytic_tag_ids' : [(6, 0, anlytic_tag_list)],
                'product_id' : product_id.id,
                'name' : sheet.cell(row,1).value,
                'price_unit' : sheet.cell(row,4).value,
#                'uom_id' : uom_id.id,
                'product_uom_id' : uom_id.id,
                'discount' : sheet.cell(row,5).value,
#                'invoice_line_tax_ids': [(6, 0, tlist)],
                'tax_ids': [(6, 0, tlist)],
#                'invoice_id': invoice_obj.id,
                'quantity' : sheet.cell(row,2).value,
            }
            invoice_obj.write({
                'invoice_line_ids': [(0, 0, vals)]
            })
#            invoice_line = invoice_line_obj.create(vals)
            row = row+1
        return True
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
