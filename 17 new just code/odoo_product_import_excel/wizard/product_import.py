# -*- coding:utf-8 -*-

import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductImportWizard(models.TransientModel):
    _name = 'product.import.wizard'
    _description = 'Product Import Wizard'

    files = fields.Binary(string="Import Excel File")
    datas_fname = fields.Char('Import File Name')

#    @api.multi #odoo13
    def import_file(self):
        category_obj = self.env['product.category']
        product_uom_obj = self.env['uom.uom']
        product_obj = self.env['product.template']
        try:
            # workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
            workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        row = 1
        plist= []
        while(row < number_of_rows):
            uom_id = product_uom_obj.search([('name', '=', sheet.cell(row,5).value)], limit=1)
            category_id = category_obj.search([('name', '=', sheet.cell(row,2).value)], limit=1)
            if not sheet.cell(row,0).value:
                raise ValidationError('%s Product name should not be empty at row number %s '%(sheet.cell(row,0).value,row))
            if not category_id:
                raise ValidationError('Product Category %s is invalid at row number %s '%(sheet.cell(row,2).value,row))
            if not uom_id:
                raise ValidationError('Product Uom %s is invalid at row number %s '%(sheet.cell(row,5).value,row))
            vals = {
                    'name': sheet.cell(row,0).value,
                    'default_code': sheet.cell(row,1).value,
                    'categ_id': category_id.id,
                    'type': sheet.cell(row,3).value,
                    'barcode': sheet.cell(row,4).value,
                    'uom_id' : uom_id.id,
                    'uom_po_id' : uom_id.id,
                    'list_price' : sheet.cell(row,7).value,
                    'standard_price' : sheet.cell(row,8).value,
                    'weight' : sheet.cell(row,9).value,
                    'volume' : sheet.cell(row,10).value,
                    'sale_ok' : sheet.cell(row,11).value,
                    'description_sale' : sheet.cell(row,12).value,
                    'description' : sheet.cell(row,13).value,
                    }
            row = row+1
            print('vals===================',vals)
            product = product_obj.create(vals)
            plist.append(product.id)
        res = self.env.ref('product.product_template_action')
        res['domain'] = str([('id','in',plist)])
        res = res.sudo().read()[0]
        return res
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
        
