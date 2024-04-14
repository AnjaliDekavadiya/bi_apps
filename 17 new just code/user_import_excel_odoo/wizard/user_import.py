# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
import urllib
from urllib.request import Request, urlopen
from odoo.exceptions import ValidationError
from odoo import models, fields, api


class ImportImageUser(models.TransientModel):
    _name = 'import.user.wizard'
    _description = 'Import User Wizard'
    
    files = fields.Binary(
        'Select Excel File (.xls / .xlsx supported)',
        required=True,
    )
    operation = fields.Selection(
        selection=[('create','Create Users'),
                    ('update','Update Users'),
        ],
        string="Operation",
        default='create',
        required=True,
    )
    
    # @api.multi
    def import_user_file(self):
        user_obj = self.env['res.users']
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
            if self.operation == 'create':
                name = sheet.cell(row,0).value
                login = sheet.cell(row,1).value
                password = sheet.cell(row,2).value
                image_medium = sheet.cell(row,3).value
                lang = sheet.cell(row,4).value
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
                    'login' : login,
                    'password':password,
                    'lang':lang,
                }
                if login:
                    user_ids = user_obj.search(
                        [('login','=',login)]
                    )

                    if user_ids :
                        raise ValidationError(
                            '%s Login User already exits row number %s in excel file.'%(
                                sheet.cell(row,1).value,row+1
                            )
                        )

                user_id = user_obj.create(vals)
                aList.insert(row-1,user_id.id)
                try:
                    vals_update = {
                        # 'image' : image,
                        'image_1920' : image,
                        }
                    user_id.write(vals_update)
                except:
                    continue

            elif self.operation == 'update':
                login = sheet.cell(row,0).value
                image_medium = sheet.cell(row,1).value
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
                    'login' : login,
                }

                if image != False:
                    vals_update = {
                    # 'image' : image,
                        'image_1920' : image,
                    }
                user_ids = user_obj.browse()
                if login:
                    user_ids = user_obj.search(
                        [('login','=',login)]
                    )
                else:
                    pass
                    
                for user_id in user_ids:
                    try:
                        vals_update = {
                        # 'image' : image,
                        'image_1920' : image,
                        }
                        user_id.write(vals_update)
                        aList.insert(row-1, user_id.id)
                    except:
                        continue
  
        action = self.env.ref('base.action_res_users').sudo().read()[0]
        action['domain'] = [('id', 'in', aList)]
        return action
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
