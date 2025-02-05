# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
from odoo import models,fields,api,_
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF           #odoo13
from datetime import datetime                                     #odoo13
from odoo.exceptions import ValidationError


class ImportHrApplicantWizard(models.TransientModel):
    
    _name = "hr.applicant.import"
    _description = 'Hr Applicant Import'

    files = fields.Binary(
        string="Import Excel File",
    )
    datas_fname = fields.Char(
       'Select Excel File'
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,default=lambda self: self.env.user.company_id,
    )
  
#     @api.multi                       #odoo13
    def import_hr_applicant_task_with_excel(self):
        
        try:
            workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        list_hr =[]
        tags_list=[]
        vals = {}
        tags=self.env['hr.applicant.category']
        contact=self.env['res.partner']
        responsible=self.env['res.users']
        degree=self.env['hr.recruitment.degree']
        medium=self.env['utm.medium']
        source=self.env['utm.source']
        job=self.env['hr.job']
        department=self.env['hr.department']
        stage=self.env['hr.recruitment.stage']
        row = 1
        while(row < number_of_rows):
            
            application_name=sheet.cell(row,0).value
            if not application_name:
                raise ValidationError('Applicant Name should not be empty at row %s in excel file.'%(row+1))

            partner_name=sheet.cell(row,1).value

            email=sheet.cell(row,3).value

            partner_id=sheet.cell(row,2).value
            if partner_id:
              customer_id = contact.search([('name', '=', partner_id),('name', '!=', False)], limit=1)
              if not customer_id:
                   customer_id = contact.search([('email', '=', email),('email', '!=', False)], limit=1)
              if not customer_id:
                  raise ValidationError('%s Contact name not found at row number %s '%(sheet.cell(row,2).value,row+1))

            Phone=sheet.cell(row,4).value

            mobile=sheet.cell(row,5).value

            type_id=sheet.cell(row,6).value
            if type_id:
                degreeObj = degree.search([('name', '=', type_id)], limit=1)
                if not degreeObj:
                    raise ValidationError('%s Degree not found at row number %s '%(sheet.cell(row,6).value,row+1))


            user_id=sheet.cell(row,7).value
            if user_id:
                responsibleObj = responsible.search([('name', '=', user_id)], limit=1)
                if not responsibleObj:
                    raise ValidationError('%s Responsible not found at row number %s '%(sheet.cell(row,7).value,row+1))

            appreciation=sheet.cell(row,8).value

            medium_id=sheet.cell(row,9).value
            if medium_id:
                mediumObj = medium.search([('name', '=', medium_id)], limit=1)
                if not mediumObj:
                    raise ValidationError('%s Medium not found at row number %s '%(sheet.cell(row,9).value,row+1))


            source_id=sheet.cell(row,10).value
            if source_id:
                sourceObj = source.search([('name', '=', source_id)], limit=1)
                if not sourceObj:
                    raise ValidationError('%s Source not found at row number %s '%(sheet.cell(row,10).value,row+1))


            referred=sheet.cell(row,11).value

            job_id=sheet.cell(row,12).value
            if job_id:
                jobObj = job.search([('name', '=', job_id)], limit=1)
                if not jobObj:
                    raise ValidationError('%s Applied Job not found at row number %s '%(sheet.cell(row,12).value,row+1))


            stage_id=sheet.cell(row,13).value
            if stage_id:
                stageObj = stage.search([('name', '=', stage_id)], limit=1)
                if not stageObj:
                    raise ValidationError('%s Stage not found at row number %s '%(sheet.cell(row,13).value,row+1))

            salary_expected = sheet.cell(row,14).value

            salary_expected_extra = sheet.cell(row,15).value

            salary_proposed = sheet.cell(row,16).value

            salary_proposed_extra = sheet.cell(row,17).value

            availability = sheet.cell(row,18).value
            availability_date = (datetime.strptime(str(availability), '%m-%d-%Y')).strftime(DF)      #odoo13

            summary = sheet.cell(row,19).value

            categ_ids=sheet.cell(row,20).value
            categ_list=categ_ids.split(',')
            tagsObj = tags.search([('name', 'in', categ_list)])

            vals = { 
                'name': application_name,
                'partner_name':partner_name,
                'email_from':email,     
                'custom_ref':referred,
                'salary_expected':salary_expected,
                'salary_expected_extra':salary_expected_extra,
                'salary_proposed':salary_proposed,
                'salary_proposed_extra':salary_proposed_extra,
                'description':summary,
                'company_id':self.company_id.id,
            }
            if appreciation == 'Normal':
                vals.update({'priority':'0'})
            if appreciation == 'Good':
                vals.update({'priority':'1'})
            if appreciation == 'Very Good':
                vals.update({'priority':'2'})
            if appreciation == 'Excellent':
                vals.update({'priority':'3'})
            if categ_ids:
                vals.update({'categ_ids':[(6,0,tagsObj.ids)]})
            if partner_id:
                vals.update({'partner_id':customer_id.id})
            if Phone:
                vals.update({'partner_phone':int(Phone)})
            if mobile:
                vals.update({'partner_mobile':int(mobile)})
            if availability:
#                 vals.update({'availability':availability})
                vals.update({'availability':availability_date})               #odoo13
            if type_id:
                vals.update({'type_id':degreeObj.id})
            if user_id:
                vals.update({'user_id':responsibleObj.id})
            if medium_id:
                vals.update({'medium_id':mediumObj.id})
            if source_id:
                vals.update({'source_id':sourceObj.id})
            if job_id:
                vals.update({'job_id':jobObj.id})
            if stage_id:
                vals.update({'stage_id':stageObj.id})
            row = row + 1
            hr_id =self.env['hr.applicant'].create(vals)
            list_hr.append(hr_id.id)
            if hr_id:
                action = self.env.ref('hr_recruitment.crm_case_categ0_act_job').sudo().read()[0]

                action['domain'] = [('id','in',list_hr)]
                action['context']={}

        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
