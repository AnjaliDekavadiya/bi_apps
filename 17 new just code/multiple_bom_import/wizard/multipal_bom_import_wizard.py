# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
import datetime

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError


class ImportbomWizard(models.TransientModel):

    _name = "multiple.bom.import"
    
    files = fields.Binary(
        string="Import Excel File",
    )
    
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.user.company_id.id,
        required=True,
    )

    method = fields.Selection(
    selection=[('variant','Import With Variant'),
                ('Without_variant','Import Without Variant'),
    ],
    string="Method",
    default='variant',
    required=True,
    )
    

    # @api.multi
    def import_multiple_bom_file_with_variant(self):
        if self.method == 'variant':
            try:
                workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
            except:
                raise ValidationError("Please select .xls/xlsx file.")
            sheet_name = workbook.sheet_names()
            sheet = workbook.sheet_by_name(sheet_name[0])
            number_of_rows = sheet.nrows
            list_multiple_bom =[]
            list_product_bom = []
            vals = {}
            excel_dict={}
            product_dict={}
            product_tmpl=self.env['product.template']
            product=self.env['product.product']
            # routing=self.env['mrp.routing']
            operationobj=self.env['stock.picking.type']
            
            row = 1

            while(row < number_of_rows):
                Number = sheet.cell(row,0).value
                product_tmpl_id = sheet.cell(row,1).value

                if product_tmpl_id in product_dict:

                    product_tmpl_id=product_dict[product_tmpl_id]
                    list_product_bom.append(product_tmpl_id)
                if Number in product_dict:
                    product_tmpl_id = product_dict.get(Number)
                if not product_tmpl_id:
                    raise ValidationError('Product name should not be empty at row %s in excel file .'%(row+1))

                if product_tmpl_id:
                    product_dict.update({Number:product_tmpl_id})
                    list_product_bom.append(product_tmpl_id)
                    product_tmpl_id=product_tmpl.search([('name', '=', product_tmpl_id)], limit=1)
                if not product_tmpl_id:
                    raise ValidationError('Invalid product name at row %s in excel file.'%(row+1))


                product_bom_id=sheet.cell(row,2).value
                if product_bom_id:
                    product_variant_id=product.search([('default_code', '=', product_bom_id)], limit=1)
                if not product_variant_id:
                    raise ValidationError('Invalid product variant code at row %s in excel file.'%(row+1))
                bom_quantity = sheet.cell(row,3).value
                if not bom_quantity:
                    raise ValidationError('Quantity should not be empty at row %s in excel file.'%(row+1))  
                
                # routingId = False
                # routing_id=sheet.cell(row,4).value
                # if routing_id:
                #     routingId=routing.search([('name', '=', routing_id)], limit=1)

                reference = sheet.cell(row,4).value

                bom_type = sheet.cell(row,5).value

                sequence=sheet.cell(row,6).value

                manufacturing_readiness = sheet.cell(row,7).value

                operation=sheet.cell(row,8).value
                if operation:
                    operation=operationobj.search([('name', '=', operation)], limit=1)

                
                if Number in excel_dict:
                    bom_id=excel_dict[Number]
                    list_multiple_bom.append(bom_id.id)
                else:

                    bom_vals = { 
                        'product_tmpl_id':product_tmpl_id.id,
                        'product_id':product_variant_id.id,
                        'product_qty':bom_quantity,
                        'company_id':self.company_id.id,
                        'code':reference,
                        'type':bom_type,
                        'sequence':sequence,
                        'ready_to_produce':manufacturing_readiness,
                        'picking_type_id':operation.id,
                        
                    }
                    # if routingId:
                    #    bom_vals.update({'routing_id':routingId.id}) 

                    bom_id =self.env['mrp.bom'].create(bom_vals)
                    excel_dict.update({Number:bom_id})
                    list_multiple_bom.append(bom_id.id)

                
                product_line_id=sheet.cell(row,9).value
                if product_line_id:
                    product_line_id=product.search([('name', '=', product_line_id)], limit=1)
                if not product_line_id:
                    raise ValidationError('Product Name should not be empty at row %s in excel file.'%(row+1))    

              
                line_quantity = sheet.cell(row,10).value
                if not line_quantity:
                    raise ValidationError('Quantity should not be empty at row %s in excel file.'%(row+1))

                operation_id=sheet.cell(row,11).value
                if operation_id:
                    operationId=self.env['mrp.routing.workcenter'].search([('name', '=', operation_id)], limit=1)

                line_vals = { 
                    'product_id':product_line_id.id,
                    'product_qty':line_quantity,
                    'bom_id':bom_id.id,
                    'operation_id':operationId.id,  
                }

                row = row + 1
                multipal_bom_line_id =self.env['mrp.bom.line'].create(line_vals)
            
            action = self.env.ref('mrp.mrp_bom_form_action').sudo().read()[0]
            action['domain'] = [('id', 'in', list_multiple_bom)]
            action['context']={}
            return action

    # @api.multi
    # def import_multiple_bom_file_without_variant(self):
        elif self.method == 'Without_variant':
            try:
                workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
            except:
                raise ValidationError("Please select .xls/xlsx file.")
            sheet_name = workbook.sheet_names()
            sheet = workbook.sheet_by_name(sheet_name[0])
            number_of_rows = sheet.nrows
            list_multiple_bom =[]
            list_product_bom = []
            vals = {}
            excel_dict={}
            product_dict={}
            product_tmpl=self.env['product.template']
            product=self.env['product.product']
            # routing=self.env['mrp.routing']
            operationobj=self.env['stock.picking.type']
            
            row = 1

            while(row < number_of_rows):
                Number = sheet.cell(row,0).value
                product_tmpl_id = sheet.cell(row,1).value

                if product_tmpl_id in product_dict:
                    product_tmpl_id=product_dict[product_tmpl_id]
                    list_product_bom.append(product_tmpl_id)
                if Number in product_dict:
                    product_tmpl_id = product_dict.get(Number)
                if not product_tmpl_id:
                    raise ValidationError('Product code should not be empty at row %s in excel file .'%(row+1))

                if product_tmpl_id:
                    product_dict.update({Number:product_tmpl_id})
                    list_product_bom.append(product_tmpl_id)
                    product_tmpl_id=product_tmpl.search([('default_code', '=', product_tmpl_id)], limit=1)
                if not product_tmpl_id:
                    raise ValidationError('Invalid product code at row %s in excel file.'%(row+1))

                bom_quantity = sheet.cell(row,2).value
                if not bom_quantity:
                    raise ValidationError('Quantity should not be empty at row %s in excel file.'%(row+1))  
                
                # routingId = False
                # routing_id=sheet.cell(row,3).value
                # if routing_id:
                #     routingId=routing.search([('name', '=', routing_id)], limit=1)

                reference = sheet.cell(row,3).value

                bom_type = sheet.cell(row,4).value

                sequence=sheet.cell(row,5).value

                manufacturing_readiness = sheet.cell(row,6).value

                operation=sheet.cell(row,7).value
                if operation:
                    operation=operationobj.search([('name', '=', operation)], limit=1)

                
                if Number in excel_dict:
                    bom_id=excel_dict[Number]
                    list_multiple_bom.append(bom_id.id)
                else:

                    bom_vals = { 
                        'product_tmpl_id':product_tmpl_id.id,
                        'product_qty':bom_quantity,
                        'company_id':self.company_id.id,
                        'code':reference,
                        'type':bom_type,
                        'sequence':sequence,
                        'ready_to_produce':manufacturing_readiness,
                        'picking_type_id':operation.id,
                        
                    }
                    # if routingId:
                    #    bom_vals.update({'routing_id':routingId.id}) 

                    bom_id =self.env['mrp.bom'].create(bom_vals)
                    excel_dict.update({Number:bom_id})
                    list_multiple_bom.append(bom_id.id)

                
                product_line_id=sheet.cell(row,8).value
                if product_line_id:
                    product_line_id=product.search([('default_code', '=', product_line_id)], limit=1)
                    
                if not product_line_id:
                    raise ValidationError('Product Code should not be empty at row %s in excel file.'%(row+1))  

              
                line_quantity = sheet.cell(row,9).value
                if not line_quantity:
                    raise ValidationError('Quantity should not be empty at row %s in excel file.'%(row+1))

                operation_id=sheet.cell(row,10).value
                if operation_id:
                    operationId=self.env['mrp.routing.workcenter'].search([('name', '=', operation_id)], limit=1)

                line_vals = { 
                    'product_id':product_line_id.id,
                    'product_qty':line_quantity,
                    'bom_id':bom_id.id,
                    'operation_id':operationId.id,  
                }

                row = row + 1
                multipal_bom_line_id =self.env['mrp.bom.line'].create(line_vals)
            
            action = self.env.ref('mrp.mrp_bom_form_action').sudo().read()[0]
            action['domain'] = [('id', 'in', list_multiple_bom)]
            action['context']={}
            return action


