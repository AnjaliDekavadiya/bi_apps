# -*- coding:utf-8 -*-

import base64
import xlrd
import datetime

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
# from openerp.exceptions import UserError
from odoo.exceptions import UserError              #odoo13

class ImportPurchaseLineWizard(models.TransientModel):
    _name = "import.purchase.line.wizard"
    _description = 'Import Purchase Line Wizard'

    files = fields.Binary(string="Import Excel File", readonly=False)#redonly
    datas_fname = fields.Char('Import File Name')

#     @api.multi                   #odoo13
    def purchase_file(self):
        active_id = self._context.get('active_id')
        purchase_id = self.env['purchase.order'].browse(active_id)
        try:
            workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        date = purchase_id.date_planned
        number_of_rows = sheet.nrows
        fpos = purchase_id.fiscal_position_id
        row = 1
        while(row < number_of_rows):
            product_id = self.env['product.product'].search([('default_code','=',sheet.cell(row,0).value)])
            
            if len(product_id) > 1:
                raise ValidationError('%s More than one product found with same product code is invalid at row number %s '%(sheet.cell(row,0).value,row+1))
            if not product_id:
                raise ValidationError('%s product code is invalid at row number %s '%(sheet.cell(row,0).value,row+1))
            
            uom_id = self.env['uom.uom'].search([('name','=',sheet.cell(row,1).value)])
            if not uom_id:
                raise ValidationError('%s product uom is invalid at row number %s '%(sheet.cell(row,1).value,row+1))
            if product_id.uom_id.category_id.id != uom_id.category_id.id:
                raise UserError(_('You try to add a product using a UoM that is not compatible with the UoM of the product. Please use an UoM in the same UoM category.'))

            tax = fpos.map_tax(product_id.supplier_taxes_id).ids

            if not product_id:
                raise ValidationError('%s product code is invalid at row number %s '%(sheet.cell(row,0).value,row+1))
            if not uom_id:
                raise ValidationError('%s product uom is invalid at row number %s '%(sheet.cell(row,1).value,row+1))
            try:
                price_unit = sheet.cell(row,2).value
            except:
                raise ValidationError('%s product price is invalid at row number %s '%(sheet.cell(row,2).value,row+1))
            try:
                product_qty = sheet.cell(row,3).value
            except:
                raise ValidationError('%s product quantity is invalid at row number %s '%(sheet.cell(row,3).value,row+1))
            try:
                po_date = sheet.cell(row,4).value
                po_date = datetime.datetime.strptime(po_date, "%m/%d/%Y")
            except:
                raise ValidationError('%s product scheduled date is invalid at row number %s '%(sheet.cell(row,4).value,row+1))
            row = row + 1
            vals = {
                'product_id' : product_id.id,
                'product_uom' : uom_id.id,
                'date_planned': po_date,
                'taxes_id' :[(6, 0, tax)],
                'name': product_id.name,
                'product_qty' : product_qty,
                'price_unit': price_unit,
                'order_id' : active_id,
                }
            self.env['purchase.order.line'].create(vals)
