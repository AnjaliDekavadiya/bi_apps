# -*- coding:utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

import base64
import xlrd

import pytz
import time
import datetime
from pytz import timezone
from datetime import datetime
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ImportMachineRepairRequestWizard(models.TransientModel):
    _name = 'import.machine.repair.request.wizard'
    _description= 'Import Machine Repair Request Wizard'

    files = fields.Binary(string="Import Excel File")
    datas_fname = fields.Char('Import File Name')

    def _convert_to_utc(self, localdatetime=None):
        check_in_date = localdatetime
        if type(localdatetime) == str:
            check_in_date = datetime.strptime(
                localdatetime, "%Y-%m-%d  %H:%M:%S")
        timezone_tz = 'utc'
        user_id = self.env.user
        if user_id.tz:
            timezone_tz = user_id.tz
        local = pytz.timezone(timezone_tz)
        local_dt = local.localize(check_in_date, is_dst=None)
        return local_dt.astimezone(pytz.utc)

    # @api.multi
    def import_machine_repair_request(self):
        user_obj = self.env['res.users']
        partner_obj = self.env['res.partner']
        project_obj = self.env['project.project']
        team_obj = self.env['machine.support.team']
        department_obj = self.env['hr.department']
        category_obj = self.env['product.category']
        product_obj = self.env['product.product']
        service_obj = self.env['service.nature']
        repair_type_obj = self.env['repair.type']
        machine_repair_obj = self.env['machine.repair.support']

        try:
            workbook = xlrd.open_workbook(
                file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(sheet_name[0])
        number_of_rows = sheet.nrows
        row = 1
        list_repair = []
        priority_dict = {
                        'low': '0',
                        'middle': '1',
                        'high': '2'
        }

        while(row < number_of_rows):
            subject = sheet.cell(row, 0).value

            if not subject:
                raise ValidationError(
                    '%s subject is invalid at row number %s ' %
                    (sheet.cell(row, 0).value, row+1))

            user_id = user_obj.search(
                [('name', '=', sheet.cell(row, 1).value)])

            if sheet.cell(row, 1).value != '' and not user_id:
                raise ValidationError(
                    '%s technician is invalid at row number %s ' %
                    (sheet.cell(row, 1).value, row+1))

            partner_id = partner_obj.search(
                [('name', '=', sheet.cell(row, 2).value)])

            if sheet.cell(row, 2).value != '' and not partner_id:
                raise ValidationError(
                    '%s customer is invalid at row number %s ' %
                    (sheet.cell(row, 2).value, row+1))

            project_id = project_obj.search(
                [('name', '=', sheet.cell(row, 3).value)])

            if sheet.cell(row, 3).value != '' and not project_id:
                raise ValidationError(
                    '%s project is invalid at row number %s ' %
                    (sheet.cell(row, 3).value, row+1))

            team_id = team_obj.search(
                [('name', '=', sheet.cell(row, 4).value)])

            if sheet.cell(row, 4).value != '' and not team_id:
                raise ValidationError(
                    '%s machine repair team is invalid at row number %s ' %
                    (sheet.cell(row, 4).value, row+1))

            department_id = department_obj.search(
                [('name', '=', sheet.cell(row, 5).value)])

            if sheet.cell(row, 5).value != '' and not department_id:
                raise ValidationError(
                    '%s department is invalid at row number %s ' %
                    (sheet.cell(row, 5).value, row+1))

            priority = priority_dict[sheet.cell(row, 6).value]

            request_date = sheet.cell(row, 7).value

            dt1 = datetime.strptime(str(request_date), "%d/%m/%Y %H:%M:%S")
            dt1 = datetime.strftime(dt1, "%Y-%m-%d %H:%M:%S")
            dt1 = self._convert_to_utc(localdatetime=dt1)
            dt1 = dt1.strftime("%Y-%m-%d %H:%M:%S")

            product_category_id = category_obj.search(
                [('name', '=', sheet.cell(row, 8).value)])

            if sheet.cell(row, 8).value != '' and not product_category_id:
                raise ValidationError(
                    '%s machine category is invalid at row number %s ' %
                    (sheet.cell(row, 8).value, row+1))

            product_id = product_obj.search(
                [('name', '=', sheet.cell(row, 9).value)])

            if sheet.cell(row, 9).value != '' and not product_id:
                raise ValidationError(
                    '%s product is invalid at row number %s ' %
                    (sheet.cell(row, 9).value, row+1))

            brand = sheet.cell(row, 10).value

            model = sheet.cell(row, 11).value

            color = sheet.cell(row, 12).value

            year = sheet.cell(row, 13).value

            damage = sheet.cell(row, 14).value

            nature_of_service_id = service_obj.search(
                [('name', '=', sheet.cell(row, 15).value)])

            if sheet.cell(row, 15).value != '' and not nature_of_service_id:
                raise ValidationError(
                    '%s nature of service is invalid at row number %s ' %
                    (sheet.cell(row, 15).value, row+1))

            repair_types_ids = repair_type_obj.search(
                [('name', 'in', sheet.cell(row, 16).value.split(','))])

            if sheet.cell(row, 16).value != '' and not repair_types_ids:
                raise ValidationError(
                    '%s repair type is invalid at row number %s ' %
                    (sheet.cell(row, 16).value, row+1))

            problem = sheet.cell(row, 17).value

            row = row + 1

            vals = {
                'subject': subject,
                'user_id': user_id.id,
                'partner_id': partner_id.id,
                'company_id': partner_id.company_id.id,
                'project_id': project_id.id,
                'team_id': team_id.id,
                'department_id': department_id.id,
                'priority': priority,
                'request_date': dt1,
                'product_category': product_category_id.id,
                'product_id': product_id.id,
                'brand': brand,
                'model': model,
                'color': color,
                'year': year,
                'damage': damage,
                'website_brand': brand,
                'website_model': model,
                'website_year': year,
                'nature_of_service_id': nature_of_service_id.id,
                'repair_types_ids': [(6, 0, repair_types_ids.ids)],
                'problem': problem,
                }
            repair_id = machine_repair_obj.new(vals)
            repair_id.onchange_partner_id()
            repair_id.onchnage_project()
            repair_id.team_id_change()

            machine_repair_vals = repair_id._convert_to_write({
                name: repair_id[name] for name in repair_id._cache
            })
            machine_repair_id = machine_repair_obj.create(machine_repair_vals)

            list_repair.append(machine_repair_id.id)

            if machine_repair_id:
                # action = self.env.ref(
                #     'machine_repair_management.action_machine_repair_support'
                #     ).sudo().read()[0]
                action = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_machine_repair_support")
                action['domain'] = [('id', 'in', list_repair)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
