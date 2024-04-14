# -*- coding:utf-8 -*-

import base64
import xlrd
import datetime

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ImportBomLineWizard(models.TransientModel):
    _name = "import.bom.line.wizard"
    _description = 'Import Bom Line Wizard'

    files = fields.Binary(
        string="Import Excel File",
        # readonly=True
    )
    datas_fname = fields.Char(
        string = 'Import File Name'
    )

#     @api.multi             #odoo13
    def bom_file(self):
        active_id = self._context.get('active_id')
        bom_id = self.env['mrp.bom'].browse(active_id)
        try:
            workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])

        number_of_rows = sheet.nrows
        row = 1
        while(row < number_of_rows):
            product_id = self.env['product.product'].search([('default_code','=',sheet.cell(row,0).value)], limit=1)
            uom_id = self.env['uom.uom'].search([('name','=',sheet.cell(row,2).value)])

            operation_id = self.env['mrp.routing.workcenter'].search([('name','=',sheet.cell(row,3).value)], limit=1)
            if not product_id:
                raise ValidationError('Component not found for Component :%s at row number %s '%(sheet.cell(row,0).value,row+1))
            try:
                product_qty = sheet.cell(row,1).value
            except:
                raise ValidationError('Quantity not found for Quantity : %s at row number %s '%(sheet.cell(row,1).value,row+1))
            if not uom_id:
                raise ValidationError('Product Unit of Measure not found for Unit of Measure : %s at row number %s '%(sheet.cell(row,2).value,row+1))
            if not operation_id:
                raise ValidationError('Consumed in Operation not found for Consumed in Operation : %s at row number %s '%(sheet.cell(row,3).value,row+1))
            row = row + 1
            vals = {
                'bom_id' : bom_id.id,
                'product_id' : product_id.id,
                'product_qty': product_qty,
                'product_uom_id': uom_id.id,
                'operation_id': operation_id.id
                }
            self.env['mrp.bom.line'].sudo().create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 

