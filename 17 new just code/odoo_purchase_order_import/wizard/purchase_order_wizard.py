# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ImportpurchaseWizard(models.TransientModel):
    _name = "import.purchase.wizard"
    _description = 'Import Purchase Wizard'

    files = fields.Binary(
        string="Import Excel File",
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
    )

#    @api.multi #odoo13
    def import_purchase_file(self):
        try:
            workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        # workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        list_purchase =[]
        vals = {}
        tags_list=tax_list=[]
        excel_dict={}

        # account_analytic_tag_obj = self.env['account.analytic.tag']
        account_tax_obj=self.env['account.tax']
        row = 1

        while(row < number_of_rows):
            partner_id = sheet.cell(row,1).value
            if partner_id:
                partner_id=self.env['res.partner'].search([('name', '=', partner_id)], limit=1)
            if not partner_id:
                raise ValidationError('Partner name should not be empty at row %s in excel file.'%(row+1))    

            currency_id = sheet.cell(row,3).value
            if currency_id:
                currency_id=self.env['res.currency'].search([('name', '=', currency_id)], limit=1)
            if not currency_id:
                raise ValidationError('Currency should not be empty at row %s in excel file.'%(row+1))    

            vender_reference = sheet.cell(row,2).value

            Number = sheet.cell(row,0).value
            if Number in excel_dict:
                purchase_id=excel_dict[Number]
                list_purchase.append(purchase_id.id)
            else:
                vals = { 
                    'partner_id':partner_id.id,
                    'partner_ref':vender_reference,
                    'currency_id':currency_id.id,
                    'company_id':self.company_id.id,
                }
                purchase_id =self.env['purchase.order'].create(vals)
                excel_dict.update({Number:purchase_id})
                list_purchase.append(purchase_id.id)

            product_id=sheet.cell(row,4).value
            if product_id:
                product_id=self.env['product.product'].search([('default_code', '=', product_id)], limit=1)
                product_uom=product_id.uom_id
            if not product_id:
                raise ValidationError('Product Code should not be empty at row %s in excel file.'%(row+1))    

            description = sheet.cell(row,5).value
            if not description:
                raise ValidationError('Product description should not be empty at row %s in excel file.'%(row+1))    

            quantity = sheet.cell(row,7).value
            if not quantity:
                raise ValidationError('Quantity should not be empty at row %s in excel file.'%(row+1))

            unit_price = sheet.cell(row,8).value
            if not unit_price:
                raise ValidationError('Unit price should not be empty at row portal %s in excel file.'%(row+1))    

            schedule_date = sheet.cell(row,6).value
            if not schedule_date:
                raise ValidationError('Product schedule date should not be empty at row %s in excel file.'%(row+1))    

            # account_analytic_id=sheet.cell(row,7).value
            # if account_analytic_id:
            #     account_analytic_id=self.env['account.analytic.account'].search([('name', '=', account_analytic_id)], limit=1)
            #analytic tags
            # tags_value=sheet.cell(row,8).value
            # tags_list=tags_value.split(',')
            # tag_ids=account_analytic_tag_obj.search([('name','in',tags_list)])

            tax_value=sheet.cell(row,9).value
            tax_list=tax_value.split(',')
            tax_ids=account_tax_obj.search([('type_tax_use', '=', 'purchase'),('name','in',tax_list), ('company_id', '=', self.company_id.id)])

            schedule_date = datetime.strptime(schedule_date, '%m/%d/%Y') #odoo13

            vals = { 
                'product_id':product_id.id,
                'name':description,
                'product_qty':quantity,
                'price_unit':unit_price,
                'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATE_FORMAT), #odoo13
                'order_id':purchase_id.id,
                'product_uom':product_uom.id,
                # 'account_analytic_id':account_analytic_id.id,
                # 'analytic_tag_ids':[(6,0,tag_ids.ids)],odoo15 22-09-2022
                'taxes_id':[(6,0,tax_ids.ids)],
                'company_id':self.company_id.id,
            }
            row = row + 1
            purchase_order_line_id =self.env['purchase.order.line'].create(vals)
        
        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        action['domain'] = [('id', 'in', list_purchase)]
        action['context']={}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
