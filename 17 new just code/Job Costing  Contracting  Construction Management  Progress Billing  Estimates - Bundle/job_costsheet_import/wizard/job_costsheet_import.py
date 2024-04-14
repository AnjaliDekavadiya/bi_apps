# -*- coding:utf-8 -*-

import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class JobCostSheetImport(models.TransientModel):
    _name = 'job.cost.sheet.import'
    
    files = fields.Binary(string="Import Excel File")
    datas_fname = fields.Char('Select Excel File')
    
    #@api.multi
    def import_job_costsheet_file(self):
        job_costsheet_obj = self.env['job.costing']
        partner_obj = self.env['res.partner']
        project_obj = self.env['project.project']
        task_obj = self.env['project.task']
        analytic_account_obj = self.env['account.analytic.account']
        costsheet_line_obj = self.env['job.cost.line']
        
        try:
            # workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
             workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        
        name = sheet.cell(1, 1).value
        partner = sheet.cell(5, 1).value
        project = sheet.cell(2, 1).value
        analytic_account = sheet.cell(3, 1).value
        task = sheet.cell(4, 1).value
        description = sheet.cell(1, 3).value
        sale_referernce = sheet.cell(2, 3).value
        notes_job = sheet.cell(7, 1).value
        
        partner_id = partner_obj.search([('name','=', partner)], limit=1)
        project_id = project_obj.search([('name','=', project)], limit=1)
        analytic_id = analytic_account_obj.search([('name','=', analytic_account)], limit=1)
        task_id = task_obj.search([('name','=', task)], limit=1)
        
        if not partner_id:
            raise ValidationError(_(
                "Partner not found for %s" %(sheet.cell(6,2).value)
            ))
            
        job_costsheet_id = job_costsheet_obj.create({
             'name': name,
             'partner_id': partner_id.id, 
             'project_id': project_id.id,
             'analytic_id': analytic_id.id,
             'task_id': task_id.id,
             'description': description,
             'so_number': sale_referernce,
             'notes_job': notes_job,
         })
        
        number_of_rows = sheet.nrows
        row = 1
        
        material_row = True
        labour_row = True
        overhead_row = True
        
        for row in range(sheet.nrows):
            if sheet.cell(row, 0).value == 'Materials':
                row = row + 2
                if material_row != False:
                    while sheet.cell(row, 0).value != 'Labours':
                        date = sheet.cell(row, 0).value
                        date = datetime.strptime(str(date), '%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
                        if not date:
                            raise ValidationError(_("Date not found for %s" %(sheet.cell(line_row, 0).value)))
                        
                        job_type_id = self.env['job.type'].search([('name','=',sheet.cell(row, 1).value)])
                        product_id = self.env['product.product'].search([('name','=', sheet.cell(row, 2).value)], limit=1)
                        reference = sheet.cell(row, 4).value
                        product_qty = sheet.cell(row, 5).value
                        
                        if not product_id:
                            raise ValidationError(_("Product not found for %s" %(sheet.cell(row, 0).value)))
                        if job_costsheet_id:
                            vals = {
                                 'date': date,
                                 'job_type_id': job_type_id.id, 
                                 'product_id': product_id.id,
                                 'reference': reference,
                                 'product_qty': product_qty,
                                 'direct_id': job_costsheet_id.id,
                                 'job_type':'material',
                            }
                            
                            jobcost_line_new = costsheet_line_obj.new(vals)
                            jobcost_line_new._onchange_product_id()
                            jcs_line_values = jobcost_line_new._convert_to_write({
                               name: jobcost_line_new[name] for name in jobcost_line_new._cache
                            })
                            jcs_line_values.update({
                                'product_qty': sheet.cell(row, 5).value,
                                'direct_id' : job_costsheet_id.id,
                            })
                            jobcostsheet_line = costsheet_line_obj.create(jcs_line_values)
                            row = row + 1
                        
        for row in range(sheet.nrows):     
            if sheet.cell(row, 0).value == 'Labours':
                row = row + 2
                if labour_row != False:
                    while sheet.cell(row, 0).value != 'Overhead':
                        date = sheet.cell(row, 0).value
                        date = datetime.strptime(str(date), '%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
                        if not date:
                            raise ValidationError(_("Date not found for %s" %(sheet.cell(line_row, 0).value)))
                        
                        job_type_id = self.env['job.type'].search([('name','=',sheet.cell(row, 1).value)])
                        product_id = self.env['product.product'].search([('name','=', sheet.cell(row, 2).value)], limit=1)
                        reference = sheet.cell(row, 4).value
                        hours = sheet.cell(row, 5).value
                        
                        if not product_id:
                            raise ValidationError(_("Product not found for %s" %(sheet.cell(row, 0).value)))
                        if job_costsheet_id:
                            vals = {
                                 'date': date,
                                 'job_type_id': job_type_id.id, 
                                 'product_id': product_id.id,
                                 'reference': reference,
                                 'hours': hours,
                                 'direct_id': job_costsheet_id.id,
                                 'job_type':'labour',
                            }
                            job_line = costsheet_line_obj.create(vals)
                            job_line._onchange_product_id()
                            row = row + 1
                        
        for row in range(sheet.nrows):
            if sheet.cell(row, 0).value == 'Overhead':
                row = row + 2
                if overhead_row != False:
                    while (row < sheet.nrows):
                        date = sheet.cell(row, 0).value
                        date = datetime.strptime(date, '%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
                        if not date:
                            raise ValidationError(_("Date not found for %s" %(sheet.cell(line_row, 0).value)))
                        
                        job_type_id = self.env['job.type'].search([('name','=',sheet.cell(row, 1).value)])
                        product_id = self.env['product.product'].search([('name','=', sheet.cell(row, 2).value)], limit=1)
                        product_qty = sheet.cell(row, 5).value
                        reference = sheet.cell(row, 4).value
                        
                        if not product_id:
                            raise ValidationError(_("Product not found for %s" %(sheet.cell(row, 0).value)))
                        if job_costsheet_id:
                            vals = {
                                 'date': date,
                                 'job_type_id': job_type_id.id, 
                                 'product_id': product_id.id,
                                 'reference': reference,
                                 'product_qty': product_qty,
                                 'direct_id': job_costsheet_id.id,
                                 'job_type':'overhead',
                                 
                            }
                            jobcost_line_new = costsheet_line_obj.new(vals)
                            jobcost_line_new._onchange_product_id()
                            jcs_line_values = jobcost_line_new._convert_to_write({
                               name: jobcost_line_new[name] for name in jobcost_line_new._cache
                            })
                            jcs_line_values.update({
                                'product_qty': sheet.cell(row, 5).value,
                                'direct_id' : job_costsheet_id.id,
                            })
                            jobcostsheet_line = costsheet_line_obj.create(jcs_line_values)
                            row = row + 1
                    
        # result = self.env.ref('odoo_job_costing_management.action_job_costing')
        # action_ref = result or False
        # action = action_ref.sudo().read()[0]
        action = self.env["ir.actions.actions"]._for_xml_id("odoo_job_costing_management.action_job_costing")
        action['domain'] = [('id', '=', job_costsheet_id.id)]
        return action
           
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
