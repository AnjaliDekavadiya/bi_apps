# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
from datetime import datetime

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError


class ImportPosWizard(models.TransientModel):

    _name = "multiple.pos.import"
    _description = "Import Multiple POS"
    
    files = fields.Binary(
        string="Import Excel File",
    )
    
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    
#    product_pricelist_id = fields.Many2one( odoo13
#        'product.pricelist',
#        string="Pricelict",
#        required=True,
#    )

#    @api.multi odoo13
    def import_multiple_pos(self):

        try:
            workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        list_multiple_pos =[]
        list_pos = []
#        vals = {} odoo13
        excel_dict={}
        product_dict={}
        pos_order =self.env['pos.order']
        pos_line_id =self.env['pos.order.line']
        session=self.env['pos.session']
        product=self.env['product.product']
        fiscal=self.env['account.fiscal.position']
        partner=self.env['res.partner']
        user=self.env['res.users']
#        pricelist=self.env['product.pricelist'] odoo13
#        price = pos_order._default_pricelist() odoo13
        
        row = 1

        while(row < number_of_rows):
            fiscal_position = False
#            taxesIds = False odoo13
#            pricelistIds = False odoo13
#            userId  = False
            Number = sheet.cell(row,0).value
            session_id = sheet.cell(row,1).value

            if session_id in product_dict:
                session_id=product_dict[session_id]
                list_pos.append(session_id)
            if Number in product_dict:
                session_id = product_dict.get(Number)
            
            session_obj_id = False
            if session_id:
                product_dict.update({Number:session_id})
                list_pos.append(session_id)
                session_obj_id=session.search([('name', '=', session_id)], limit=1)
                if not session_obj_id:
                    raise ValidationError('Session %s is not found or in close state at row %s in excel file.' %(session_id, row+1))
     
            order_date = sheet.cell(row,2).value

            fiscal_id=sheet.cell(row,3).value
            if fiscal_id:
                fiscal_position=fiscal.search([('name', '=', fiscal_id)], limit=1)

            partnerId = False
            partner_id=sheet.cell(row,4).value
            if partner_id:
                partnerId=partner.search([('name', '=', partner_id)], limit=1)
                if not partnerId:
                    raise ValidationError('Partner name should not be match at row %s in excel file .'%(row+1))

            userId = False
            user_id=sheet.cell(row,9).value  
            if user_id:
                userId=user.search([('name', '=', user_id)], limit=1)
                if not userId:
                    raise ValidationError('user name should not be match at row %s in excel file .'%(row+1))


            if Number in excel_dict:
                pos_id=excel_dict[Number]
                list_multiple_pos.append(pos_id.id)
            else:
                pos_vals = {
#                    'session_id':session_obj_id and session_obj_id.id or False, odoo13
                    'session_id':session_obj_id.id,
                    'date_order':order_date,
                    'company_id':self.company_id.id,
                    'amount_tax' : 0.0,
                    'amount_total' : 0.0,
                    'amount_paid' : 0.0,
                    'amount_return' : 0.0,
#                    'pricelist_id':price, odoo13
#                    'pricelist_id':self.product_pricelist_id.id, odoo13
                    
                }
                if fiscal_position:
                   pos_vals.update({'fiscal_position_id':fiscal_position.id})
                if partnerId:
                    pos_vals.update({'partner_id':partnerId.id})
                if userId:
                    pos_vals.update({'user_id':userId.id})


                poss = pos_order.new(pos_vals)
#                poss._onchange_amount_all() odoo13
                poss._onchange_partner_id()
                pos_vals = poss._convert_to_write({
                          name: poss[name] for name in poss._cache
                })

#                pos_vals.update({'session_id':session_obj_id and session_obj_id.id or False}) odoo13
                pos_id =pos_order.create(pos_vals)
                excel_dict.update({Number:pos_id})
                list_multiple_pos.append(pos_id.id)

            
            product_line_id=sheet.cell(row,5).value
            if not product_line_id:
                raise ValidationError('Product name should not be empty at row %s in excel file .'%(row+1))
   
            if product_line_id:
                product_lineId=product.search([('name', '=', product_line_id)], limit=1)
            if not product_lineId:
                raise ValidationError('Product name should not be match at row %s in excel file .'%(row+1))
   
          
            line_quantity = sheet.cell(row,6).value
        
            price_unit=sheet.cell(row,7).value

            discount=sheet.cell(row,8).value

            line_vals = {
                'product_id':product_lineId.id,
                'full_product_name':product_lineId.name,
                'qty':line_quantity,
                'order_id':pos_id.id,
                'discount':discount,
            }
            line = pos_line_id.new(line_vals)
#            line._onchange_amount_line_all() odoo13
            line._onchange_product_id()
            line._onchange_qty()
            line_vals = line._convert_to_write({
                      name: line[name] for name in line._cache
            })
            line_vals.update({'company_id':self.company_id.id})
            line_vals.update({'price_unit':price_unit})
            row = row + 1
            multipal_pos_line_id =pos_line_id.create(line_vals)
#            odoo13
            # multipal_pos_line_id._onchange_amount_line_all()
            pos_line_id._onchange_amount_line_all()
            pos_id._onchange_amount_all()
            pos_id._compute_batch_amount_all()
        
        action = self.env.ref('point_of_sale.action_pos_pos_form').sudo().read()[0]
        action['domain'] = [('id', 'in', list_multiple_pos)]
        action['context']={}
        return action

