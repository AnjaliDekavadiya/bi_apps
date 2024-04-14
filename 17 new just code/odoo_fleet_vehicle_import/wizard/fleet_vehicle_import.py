# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF           #odoo13
from datetime import datetime                                     #odoo13

class ImportFleetVehicleWizard(models.TransientModel):
    _name = 'import.fleet.vehicle.wizard'

    files = fields.Binary(string="Import Excel File")
    datas_fname = fields.Char('Import File Name')

#     @api.multi               #odoo13
    def import_fleet_vehicle(self):
        vehicle_model_obj = self.env['fleet.vehicle.model']
        vehicle_model_brand_obj = self.env['fleet.vehicle.model.brand']
        partner_obj = self.env['res.partner']
        company_obj = self.env['res.company']
        vehicle_obj = self.env['fleet.vehicle']
        user_obj = self.env['res.users']                   #odoo13
        try:
            workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.files))
        except:
            raise ValidationError("Please select .xls/xlsx file...")
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows
        row = 1
        list_vehicle = []
        attr_dict = {}

        while(row < number_of_rows):
            name = sheet.cell(row,0).value
            split_val = name.split('/')
            brand_name = split_val[0]
            model_name = split_val[1]
            
            model_id = vehicle_model_obj.search([('name', '=', model_name),('brand_id.name', '=', brand_name)])
            if not model_id:
                raise ValidationError('%s vehicle model is invalid at row number %s '%(sheet.cell(row,0).value,row+1))
            
            license_plate = sheet.cell(row,1).value
            
            driver_id = partner_obj.search([('name', '=', sheet.cell(row,2).value)])
            if not driver_id:
                raise ValidationError('%s driver is invalid at row number %s '%(sheet.cell(row,2).value,row+1))
            
            location = sheet.cell(row,3).value
            
            chassis_number = sheet.cell(row,4).value
            
            model_year = sheet.cell(row,5).value
            
            odometer = sheet.cell(row,6).value
            
            odometer_unit = sheet.cell(row,7).value
            if not odometer_unit:
                raise ValidationError('%s odometer unit is invalid at row number %s '%(sheet.cell(row,8).value,row+1))
            
            acquisition_date = sheet.cell(row,8).value
            custom_acquisition_date = (datetime.strptime(str(acquisition_date), '%m/%d/%Y')).strftime(DF)      #odoo13
            
            first_contract_date = sheet.cell(row,9).value
            custom_first_contract_date = (datetime.strptime(str(first_contract_date), '%m/%d/%Y')).strftime(DF)      #odoo13
            
            car_value = sheet.cell(row,10).value
            
            residual_value = sheet.cell(row,11).value
            
            seats = sheet.cell(row,12).value
            
            doors = sheet.cell(row,13).value
            
            color = sheet.cell(row,14).value
            
            transmission = sheet.cell(row,15).value
            
            fuel_type = sheet.cell(row,16).value
            
            co2 = sheet.cell(row,17).value
            
            horsepower = sheet.cell(row,18).value
            
            horsepower_tax = sheet.cell(row,19).value
            
            power = sheet.cell(row,20).value
            
            future_driver_id = partner_obj.search([('name', '=', sheet.cell(row,21).value)])      #odoo13
            if not future_driver_id:
                raise ValidationError('%s Future Driver is invalid at row number %s '%(sheet.cell(row,21).value,row+1))
            
            manager_id = user_obj.search([('name', '=', sheet.cell(row,22).value)])              #odoo13
            if not manager_id:
                raise ValidationError('%s Manager is invalid at row number %s '%(sheet.cell(row,22).value,row+1))
            
            next_assignation_date = sheet.cell(row,23).value                #odoo13
            custom_next_assignation_date = (datetime.strptime(str(next_assignation_date), '%m/%d/%Y')).strftime(DF)
            
            net_car_value = sheet.cell(row,24).value                #odoo13
            
            row = row + 1
            
            vals = {
                'model_id': model_id.id,
                'license_plate': license_plate,
                'driver_id': driver_id.id,
                'location': location,
                'vin_sn' : chassis_number,
                'model_year': model_year,
                'company_id': driver_id.company_id.id,
                'odometer': odometer,
                'odometer_unit': odometer_unit,
#                 'acquisition_date': acquisition_date,
                'acquisition_date': custom_acquisition_date,            #odooo13
#                'first_contract_date': first_contract_date,
                'first_contract_date': custom_first_contract_date,      #odooo13
                'car_value': car_value,
                'residual_value': residual_value,
                'seats': seats,
                'doors': doors,
                'color': color,
                'transmission': transmission,
                'fuel_type': fuel_type,
                'co2': co2,
                'horsepower': horsepower,
                'horsepower_tax': horsepower_tax,
                'power': power,
                'future_driver_id': future_driver_id.id,                   #odooo13
                'manager_id' : manager_id.id,                              #odooo13
                'next_assignation_date': custom_next_assignation_date,     #odooo13    
                'net_car_value' : net_car_value,                           #odooo13
                }
            vehicle_id = vehicle_obj.create(vals)
            
            list_vehicle.append(vehicle_id.id)
            
            if vehicle_id:
                action = self.env.ref('fleet.fleet_vehicle_action').sudo().read()[0]
                action['domain'] = [('id','in',list_vehicle)]
        return action
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
