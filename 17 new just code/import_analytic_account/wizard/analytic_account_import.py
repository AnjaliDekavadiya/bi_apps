# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
import datetime

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ImportAnalyticAccount(models.TransientModel):
    _name = "import.analytic.account"
    _description = 'Import Analytic Account'

    files = fields.Binary(
        string="Import Excel File",
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
    )
  
#     @api.multi              #odoo13
    def analytic_account_with_excel(self):
       
        try:
            workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        list_analytic = []
        vals = {}
        customer_obj = self.env['res.partner']
        # account_analytic_group_obj = self.env['account.analytic.group']
        analytic_plan_obj = self.env['account.analytic.plan']
        row = 1
        while(row < number_of_rows):
            
            analytic_account = sheet.cell(row,0).value
            if not analytic_account:
                raise ValidationError('Analytic Account name should not be empty at row %s in excel file .'%(row+1))

           
            reference = sheet.cell(row,1).value
            
            
            partner_id = sheet.cell(row,2).value
            if partner_id:
                partner = customer_obj.search([('name', '=', partner_id)], limit=1)

            # group_id = sheet.cell(row,3).value
            # if group_id:
            #     group = account_analytic_group_obj.search([('name', '=', group_id)], limit=1)
           
            plan_id = sheet.cell(row,3).value
            if plan_id:
                 plan = analytic_plan_obj.search([('name', '=', plan_id)], limit=1)
           

            vals = { 
                'name': analytic_account,
                'code':reference,
                'company_id':self.company_id.id,
            }
            if partner:
                vals.update({'partner_id':partner.id})
            # if group:
            #     vals.update({'group_id':group.id})
            if plan:
                 vals.update({'plan_id':plan.id})

            row = row + 1
            analytic_id = self.env['account.analytic.account'].create(vals)
           
            list_analytic.append(analytic_id.id)
            if analytic_id:
                action = self.env.ref('analytic.action_account_analytic_account_form').sudo().read()[0]

                action['domain'] = [('id','in',list_analytic)]

        return action
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

   
