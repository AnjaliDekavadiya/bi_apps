# -*- coding: utf-8 -*-

import base64
import xlrd
import sys

from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api

class ImportCustomerSupplier(models.TransientModel):
    _name = 'import.customer.supplier'
    
    files = fields.Binary(
        'Select Excel File (.xls / .xlsx supported)',
    )
    
    # @api.multi
    def import_file(self):
        partner_obj = self.env['res.partner']
        state_obj = self.env['res.country.state']
        country_obj = self.env['res.country']
        user_obj = self.env['res.users']
        company_obj = self.env['res.company']
        price_list_obj = self.env['product.pricelist']
        payment_term_obj = self.env['account.payment.term']
       
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
        
            name = sheet.cell(row,0).value
            company_type = False
            parent = False
            state = False
            country = False
            price_list = False
            
            if sheet.cell(row,1).value:
                company_type = sheet.cell(row,1).value

                if company_type not in ['person','company']:
                    company_type = 'person'
                    
                if company_type == 'company':
                    is_company = True
                else:
                    is_company = False
                    
                    
            if sheet.cell(row,2).value:
                parent = partner_obj.search([('name','=',sheet.cell(row,2).value)])
                #print("=======================parent================================",parent)
                if parent:
                    if not parent.is_company:
                        raise UserError("Parent Is Incorrect")
                if not parent:
                    raise UserError("Parent Not Available")
                parent = parent.id
            
            # if sheet.cell(row,6).value:
            #     #print("rdftgyhujkop",sheet.cell(row,6).value)
            #     state = state_obj.search([('name','=',sheet.cell(row,6).value)])
            #     #print("state--------",state)
            #     if not state:
            #         raise UserError('Please Add correct State')
            #     state = state.id


            if sheet.cell(row, 6).value:
                state = state_obj.search([('name', '=', sheet.cell(row, 6).value)], limit=1)
                
                if not state:
                    raise UserError('Please Add correct State')
                
                state = state.id







            
            if sheet.cell(row,7).value:
                country = country_obj.search([('name','=',sheet.cell(row,7).value)])
                if not country:
                    raise UserError('Please Add correct Country')
                country = country.id
            
            # if sheet.cell(row,19).value:
            #     price_list = price_list_obj.search([('name','=',sheet.cell(row,19).value)])
            #     if not price_list:
            #         raise UserError('Invalid Price list')

            if sheet.cell(row,17).value:
                price_list = price_list_obj.search([('name','=',sheet.cell(row,17).value)])
                #print("=====================price_list==========================",price_list)
                if not price_list:
                    raise UserError('Invalid Price list')
            
            # payment_term_list = sheet.cell(row,20).value  
            # if payment_term_list:
            #     payment_term_list = payment_term_obj.search([('name','=',sheet.cell(row,20).value)])
            #     if not payment_term_list:
            #         raise UserError('Invalid Payment Term.')

            payment_term_list = sheet.cell(row,18).value  
            #print("==================payment_term_list===================",payment_term_list)
            if payment_term_list:
                payment_term_list = payment_term_obj.search([('name','=',sheet.cell(row,18).value)])
                print("111111111111111111",sheet.cell(row,18).value)
                if not payment_term_list:
                    raise UserError('Invalid Payment Term.')

            payment_vendor_term_list = sheet.cell(row,19).value  
            #print("==========================payment_vendor_term_list=========================",payment_vendor_term_list)
            if payment_vendor_term_list : 
                payment_vendor_term_list = payment_term_obj.search([('name','=',sheet.cell(row,19).value)])

                if not payment_vendor_term_list:
                    raise UserError('Invalid Payment Term.')
            
            # company = company_obj.search([('name','=',sheet.cell(row,21).value)])
            company = company_obj.search([('name','=',sheet.cell(row,15).value)])
            #print("======================company========================",company)
            if company:
                company = company.id
                
            # sales_person = user_obj.search([('name','=',sheet.cell(row,16).value)])
            sales_person = user_obj.search([('name','=',sheet.cell(row,14).value)])
            #print("======================sales_person======================",sales_person)
            if sales_person:    
                sales_person = sales_person.id
            zip_code = sheet.cell(row,8).value
            if zip_code:
                zip_code = int(zip_code)
            phone = sheet.cell(row,10).value
            if phone:
                phone = int(phone)
            mobile = sheet.cell(row,11).value
            if mobile:
                mobile = int(mobile)
                
                    
            street1 = sheet.cell(row,3).value
            street2 = sheet.cell(row,4).value
            city = sheet.cell(row,5).value
            website = sheet.cell(row,9).value
            email = sheet.cell(row,12).value
            comment = sheet.cell(row,13).value
            # customer = sheet.cell(row,14).value
            # supplier = sheet.cell(row,15).value
            # Internal_ref = sheet.cell(row,20).value
            Internal_ref = sheet.cell(row,16).value
            
            row = row+1
            vals = {
                    'name':name,
                    'company_type' : company_type,
                    'is_company':is_company,
                    'parent_id':parent,
                    'street' : street1,
                    'street2': street2,
                    'city':city,
                    'state_id':state,
                    'country_id':country,
                    'zip':zip_code,
                    'website':website,
                    'phone':phone,
                    'mobile':mobile,
                    'email':email,
                    'comment':comment,
                    # 'customer':customer,
                    # 'supplier':supplier,
                    'user_id':sales_person,
                    'property_product_pricelist':price_list,
                    'ref':Internal_ref,
                    'company_id':company,
                    'property_payment_term_id':payment_term_list,
                    'property_supplier_payment_term_id':payment_vendor_term_list,
                    }
            partner_id = partner_obj.create(vals)
            partner_id = partner_id.id
            aList.insert(row-1,partner_id)
            
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer - Supplier',
            'res_model': 'res.partner',
            'res_id': partner_id,
            'domain': "[('id','in',[" + ','.join(map(str, aList)) + "])]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target' : partner_id,
        }
            
