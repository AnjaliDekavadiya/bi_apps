# -*- coding:utf-8 -*-

import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ImportOrderLineWizard(models.TransientModel):
    _name = 'import.order.line.wizard'

    files = fields.Binary(string="Import Excel File")
    datas_fname = fields.Char('Import File Name')

    # @api.multi
    def import_file(self):
        active_id = self._context.get('active_id')
        product_obj = self.env['product.product']
        product_uom_obj = self.env['uom.uom']
        sale_order_line_obj = self.env['sale.order.line']
        try:
            workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        row = 1
        while(row < number_of_rows):
            uom_id = product_uom_obj.search([('name', '=', sheet.cell(row,1).value)])
            product_id = product_obj.search([('default_code', '=', sheet.cell(row,0).value)])
            if not uom_id:
                raise ValidationError('%s product uom is invalid at row number %s '%(sheet.cell(row,1).value,row+1))
            if not product_id:
                raise ValidationError('%s product code is invalid at row number %s '%(sheet.cell(row,0).value,row+1))
            try:
                product_qty = sheet.cell(row,2).value
                product_qty = product_qty
            except:
                raise ValidationError('%s product quantity is invalid at row number %s '%(sheet.cell(row,2).value,row+1))
            row = row+1
            vals = {
                    'product_id': product_id.id,
                    'product_uom' : uom_id.id,
                    'product_uom_qty' : product_qty,
                    'order_id': active_id
                    }
            sale_order_line_obj.create(vals)
