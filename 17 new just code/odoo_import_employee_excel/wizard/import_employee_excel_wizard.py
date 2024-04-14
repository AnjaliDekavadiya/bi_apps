# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
import base64
import xlrd
import urllib
from urllib.request import Request, urlopen
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

class ImportemployeeWizard(models.TransientModel):
    _name = "import.employee.wizard"
    _description = 'Import Employee Wizard'

    files = fields.Binary(
        string='Select Excel File (.xls / .xlsx supported)'
    )

    # @api.multi #odoo13
    def import_employee_file(self):
        try:
            workbook = xlrd.open_workbook(file_contents = base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file.")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        aList =[]
        row = 1
        while(row < number_of_rows):
            name = sheet.cell(row,0).value
            
            if name:
                name_already = self.env['hr.employee'].search([('name', '=', name)], limit=1)
                if name_already:
                    raise ValidationError(
                        '%s Employee already exits row number %s in excel file.'%(
                            sheet.cell(row,0).value,row+1
                        )
                    )

            if not name:
                raise ValidationError(
                    '%s Name should not be empty at row number %s in excel file.'%(
                        sheet.cell(row,0).value,row+1
                    )
                )

            work_email = sheet.cell(row,1).value

            identification = int(sheet.cell(row,2).value)
            
            birthday = sheet.cell(row,3).value
            birthday = datetime.strptime(birthday, '%m/%d/%Y')
            birthday = birthday.strftime(DEFAULT_SERVER_DATE_FORMAT)

            gender = sheet.cell(row,4).value

            work_location_id = sheet.cell(row,5).value
            if work_location_id:
                work_location_id = self.env['hr.work.location'].search([('name', '=', work_location_id)], limit=1)
    
            work_location = sheet.cell(row,5).value

            Mobile = int(sheet.cell(row,6).value)

            Phone = sheet.cell(row,7).value

            job_title = sheet.cell(row,8).value
            
            passport_id = int(sheet.cell(row,9).value)
            
            emergency_contact = int(sheet.cell(row,10).value)

            emergency_phone = sheet.cell(row,11).value

            km_home_work = sheet.cell(row,12).value

            marital_status = sheet.cell(row,13).value

            place_of_birth = sheet.cell(row,14).value
            
            study_school = sheet.cell(row,15).value

            study_field = sheet.cell(row,16).value

            department_id = sheet.cell(row,17).value
            if department_id:
                department_id=self.env['hr.department'].search([('name', '=', department_id)], limit=1)

            job_id = sheet.cell(row,18).value
            if job_id:
                job_id=self.env['hr.job'].search([('name', '=', job_id)], limit=1)

            image_medium = sheet.cell(row,19).value

            if 'http' in image_medium or 'https' in image_medium:
                try:
                    image_url_header = Request(
                        image_medium, headers={
                            'User-Agent': 'Mozilla/5.0'
                        }
                    )
                    image = base64.encodebytes(
                        urllib.request.urlopen(
                            image_url_header
                        ).read()
                    )
                except:
                    image = False
            else:
                try:
                    image = base64.b64encode(
                        open(
                            image_medium, 'rb'
                        ).read()
                    )
                except:
                    image = False
            row = row+1
            vals = { 
                'name': name,
                'work_email':work_email,
                'identification_id':identification,
                # 'work_location':work_location,
                'work_location_id':work_location_id.id,
                'mobile_phone':Mobile,
                'work_phone':Phone,
                'job_title':job_title,
                'passport_id':passport_id,
                'emergency_contact':emergency_contact,
                'emergency_phone':emergency_phone,
                'km_home_work':km_home_work,
                'birthday':birthday,
                'gender':gender,
                'marital':marital_status,
                'place_of_birth':place_of_birth,
                'study_school':study_school,
                'study_field':study_field,
                # 'user_id':user_id.id,
                'department_id':department_id.id,
                'job_id':job_id.id,    
            }
            employee_id =self.env['hr.employee'].create(vals)
            if employee_id:
                employee_id.write({'name': name})
            aList.insert(row-1,employee_id.id)
            try:
                vals_update = {
                    'image_1920' : image,
                    }
                employee_id.write(vals_update)
            except:
                continue

        action = self.env.ref('hr.open_view_employee_list_my').sudo().read()[0]
        action['domain'] = [('id','in',aList)]
        return action


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
