# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
import base64
import xlrd
import urllib
from urllib.request import Request, urlopen
from odoo.exceptions import ValidationError
from odoo import models, fields, api


class ImportImageEmployee(models.TransientModel):
    _name = 'import.employee.template'
    _description = 'Import Image Employee'
    
    files = fields.Binary(
        'Select Excel File (.xls / .xlsx supported)',
        required=True,
    )
    operation = fields.Selection(
        selection=[('create','Create Employee'),
                    ('update','Update Employee'),
        ],
        string="Operation",
        default='create',
        required=True,
    )
    
#    @api.multi #odoo13
    def import_employee_file(self):
        employee_obj = self.env['hr.employee']
        try:
            workbook = xlrd.open_workbook(
                file_contents=base64.decodebytes(
                    self.files
                )
            )
        except:
            raise ValidationError("Please select .xls/xlsx file...")
            
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        aList = []
        row = 1
        while(row < number_of_rows):
            name = sheet.cell(row,0).value
            reference = sheet.cell(row,1).value
            image_medium = sheet.cell(row,2).value
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
                'name' : name,
                'identification_id' : reference,
            }
                    
            if self.operation == 'create':
                template_id = employee_obj.create(vals)
                aList.insert(row-1,template_id.id)
                try:
                    vals_update = {
                        'image_1920' : image,
                        }
                    template_id.write(vals_update)
                except:
                    continue
            
            elif self.operation == 'update':
                if image != False:
                    vals_update = {
                            'image_1920' : image,
                            }
                template_ids = employee_obj.browse()
                if reference:
                    template_ids = employee_obj.search(
                        [('identification_id','=',reference)]
                    )
                elif name:
                    template_ids = employee_obj.search(
                        [('name','=',name)]
                    )
                else:
                    pass
                    
                for template_id in template_ids:
                    try:
                        vals_update = {
                            'image_1920' : image,
                        }
                        template_id.write(vals_update)
                        aList.insert(row-1, template_id.id)
                    except:
                        continue
        action = self.env.ref('hr.open_view_employee_list_my').sudo().read()[0]
        action['domain'] = [('id', 'in', aList)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
