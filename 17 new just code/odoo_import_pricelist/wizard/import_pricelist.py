# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import xlrd
import base64
from datetime import datetime #odoo13
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT #odoo13


class ImportPricelistWizard(models.TransientModel):
    _name = 'import.pricelist.wizard'
    _description = 'Import Pricelist Wizard'
   
    import_product_by = fields.Selection(
        [('name','Name'),
         ('code','Code'),
         ('barcode','Barcode')],
        string='Import Product By',
        default='name',
    )
    import_product_variants_by = fields.Selection(
        [('name','Name'),
         ('code','Code'),
         ('barcode','Barcode')],
        string='Import Product Variants By',
        default='code',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    files = fields.Binary(
        string="Import Excel File"
    )
    datas_fname = fields.Char(
        'Select Excel File'
    )
    
#    @api.multi #odoo13
    def import_pricelist_file(self):
        pricelists_lists = []
        product_pricelist_obj = self.env['product.pricelist']
        product_category = self.env['product.category']
        product_pricelist_item = self.env['product.pricelist.item']
        excel_dict={}
        row = 1
        try:
            workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls file...")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        while(row < number_of_rows):
            pricelist_unique_name = sheet.cell(row,0).value
            pricelist_name = sheet.cell(row,1).value
            currency_name = sheet.cell(row,2).value
            pricelistId = False
            if pricelist_unique_name :
                if not pricelist_name :
                    raise ValidationError('Pricelist Name is not found at row number %s '%int(row+1))
                if not currency_name:
                    raise ValidationError('Currency is not fount at row number %s'%int(row+1))
                currency_id = self.env['res.currency'].search([('name','=',currency_name)], limit=1)
                if not currency_id:
                    raise ValidationError('%s This currency is not found.'%(currency_name))
                vals = {
                    'name' : pricelist_name,
                    'company_id' : self.company_id.id,
                    'currency_id': currency_id.id,
                }
                pricelistId = product_pricelist_obj.create(vals);
                pricelists_lists.append(pricelistId.id)
                excel_dict.update({pricelist_unique_name:pricelistId})
                pricelist_row_number = row
            else:
                pricelist_name = sheet.cell(pricelist_row_number,0).value
                pricelistId = excel_dict[pricelist_name]
            applied_on_value = sheet.cell(row,3).value
            applied_on_value_str = str(applied_on_value)
            if pricelistId:
                min_quantity_name = sheet.cell(row,7).value
                start_date = sheet.cell(row,8).value
                end_date = sheet.cell(row,9).value
                compute_price_value = sheet.cell(row,10).value
                item_vals = {
                    'pricelist_id' : pricelistId.id,
                    'min_quantity' : int(min_quantity_name),
#                    'date_start' : start_date,
#                    'date_end' : end_date,
                }
                if start_date:
                    start_date = datetime.strptime(start_date, '%m/%d/%Y') #odoo13
                    item_vals.update({
                        'date_start' : start_date.strftime(DEFAULT_SERVER_DATE_FORMAT), #odoo13
                    })
                if end_date:
                    end_date = datetime.strptime(end_date, '%m/%d/%Y') #odoo13
                    item_vals.update({
                        'date_end' : end_date.strftime(DEFAULT_SERVER_DATE_FORMAT), #odoo13
                    })                
                if applied_on_value_str == 'Global':
#                    print(type(applied_on_value),applied_on_value)
                    applied_on_value_key = '3_global'
                    item_vals.update({'applied_on' : str(applied_on_value_key)})
                if applied_on_value_str == 'Product Category':
                    applied_on_value_key = '2_product_category'
                    categ_id_name = sheet.cell(row,4).value
                    if not categ_id_name:
                        raise ValidationError("Product Category is not found at row number %s"%int(row+1))
                    if categ_id_name:
                        categID = product_category.search([('name','=',categ_id_name)], limit = 1)
                    if not categID:
                        raise ValidationError("%s Product Category is not found"%(categ_id_name))
                    else:
                        item_vals.update({'categ_id' : categID.id})
                    item_vals.update({'applied_on' : str(applied_on_value_key)})
                if applied_on_value_str == 'Product':
                    applied_on_value_key = '1_product'
                    product_tmpl_name = sheet.cell(row,5).value
                    if not product_tmpl_name:
                        raise ValidationError("Product is not found at row number %s"%int(row+1))
                    if self.import_product_by == 'name' and product_tmpl_name:
                        productTempID = self.env['product.template'].search([('name','=',product_tmpl_name)], limit=1)
                    elif self.import_product_by == 'code' and product_tmpl_name:
                        productTempID = self.env['product.template'].search([('default_code','=',product_tmpl_name)], limit=1)
                    elif self.import_product_by == 'barcode' and product_tmpl_name:
                        productTempID = self.env['product.template'].search([('barcode','=',product_tmpl_name)], limit=1)
                    if not productTempID:
                        raise ValidationError("%s Product is not found"%(product_tmpl_name))
                    else:
                        item_vals.update({'product_tmpl_id':productTempID.id})
                    item_vals.update({'applied_on' : str(applied_on_value_key)})
                if applied_on_value_str == 'Product Variant':
                    applied_on_value_key = '0_product_variant'
                    product_name = sheet.cell(row,6).value
                    if not product_name:
                        raise ValidationError("Product Variant is not found at row number %s"%int(row+1))
                    if self.import_product_variants_by == 'name' and product_name:
                        productID = self.env['product.product'].search([('name','=',product_name)], limit=1)
                    elif self.import_product_variants_by == 'code' and product_name:
                        productID = self.env['product.product'].search([('default_code','=',product_name)], limit=1)
                    elif self.import_product_variants_by == 'barcode' and product_name:
                        productID = self.env['product.product'].search([('barcode','=',product_name)], limit=1)
                    if not productID:
                        raise ValidationError("%s Product Variant is not found"%(product_name))
                    else:
                        item_vals.update({'product_id':productID.id})
                    item_vals.update({'applied_on' : str(applied_on_value_key)})
                if compute_price_value == 'Fix Price':
                    fixed_price_value = sheet.cell(row,11).value
                    if not fixed_price_value:
                        raise ValidationError("Fixed Price is not found at row number %s"%(int(row+1)))
                    else:
                        item_vals.update({'fixed_price' : fixed_price_value})
                    item_vals.update({'compute_price' : 'fixed'})
                if compute_price_value == 'Percentage':
                    percentage_value = sheet.cell(row,12).value
                    if not percentage_value:
                        raise ValidationError("Percentage (discount) is not found at row number %s"%(int(row+1)))
                    else:
                        item_vals.update({'percent_price' : float(percentage_value)})
                    item_vals.update({'compute_price' : 'percentage'})
                if compute_price_value == 'Formula':
                    based_on_value = sheet.cell(row,13).value
                    price_discount_value = sheet.cell(row,14).value
                    price_surcharge_value = sheet.cell(row,15).value
                    rounding_method_value = sheet.cell(row,16).value
                    min_margin_value = sheet.cell(row,17).value
                    max_margin_value = sheet.cell(row,18).value
                    item_vals.update({'compute_price' : 'formula'})
                    if not based_on_value:
                        raise ValidationError("Based On is not found at row number %s"%(int(row+1)))
                    else:
                        item_vals.update({
                            'price_discount' : price_discount_value,
                            'price_surcharge' : price_surcharge_value,
                            'price_round' : rounding_method_value,
                            'price_min_margin' : min_margin_value,
                            'price_max_margin' : max_margin_value,
                        })
                        if based_on_value == 'Cost':
                            item_vals.update({'base' : 'standard_price'})
                        if based_on_value == 'Public Price':
                            item_vals.update({'base' : 'list_price'})
                        if based_on_value == 'Other Pricelist':
                            item_vals.update({'base' : 'pricelist'})
            item_id = product_pricelist_item.create(item_vals)
            row += 1
        action = self.env.ref('product.product_pricelist_action2').sudo().read()[0]
        action['domain'] = [('id', 'in', pricelists_lists)]
        return action
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: