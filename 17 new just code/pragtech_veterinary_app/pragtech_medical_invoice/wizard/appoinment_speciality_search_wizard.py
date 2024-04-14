# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime


class MedicalAppointmentWizard(models.TransientModel):
    _name = "medical.appointment.wizard"
    
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    speciality_id = fields.Many2one('medical.speciality', 'Speciality', required=True)

    def search_appointment(self):
        appoinment_obj = self.env['medical.appointment']
        appoinment_id_list=[]
        for res in self:
            record = appoinment_obj.search([('speciality', '=', res.speciality_id.id)])
            for rec in record:
                rec_startdate = datetime.strptime(str(rec.appointment_sdate), '%Y-%m-%d %H:%M:%S')
                if res.start_date != False and res.end_date != False:
                    s_date = datetime.strptime(str(res.start_date), '%Y-%m-%d').date()
                    e_date = datetime.strptime(str(res.end_date), '%Y-%m-%d').date()
                    app_date = datetime.strptime(str(rec.appointment_sdate[0:10]), '%Y-%m-%d').date()
                    if app_date <= e_date and app_date >= s_date and rec.validity_status == 'invoiced':
                        appoinment_id_list.append(rec.inv_id.id)
                elif res.start_date != False and res.end_date == False:
                    s_date = datetime.strptime(str(res.start_date), '%Y-%m-%d').date()
                    e_date = False
                    app_date = datetime.strptime(str(rec.appointment_sdate[0:10]), '%Y-%m-%d').date()
                if app_date >= s_date and rec.validity_status == 'invoiced':
                    appoinment_id_list.append(rec.inv_id.id)
                elif res.start_date == False and res.end_date != False:
                    s_date = False
                    e_date = datetime.strptime(str(res.end_date), '%Y-%m-%d').date()
                    app_date = datetime.strptime(str(rec.appointment_sdate[0:10]), '%Y-%m-%d').date()
                    if app_date <= e_date and rec.validity_status == 'invoiced':
                        appoinment_id_list.append(rec.inv_id.id)
                else:
                    if rec.validity_status == 'invoiced':
                        appoinment_id_list.append(rec.inv_id.id)
        imd = self.env['ir.model.data']
        res_id = imd._xmlid_to_res_id('account.view_move_tree')
        res_id_form = imd._xmlid_to_res_id('account.view_move_form')
        
        result = {
            'name': 'Create invoice',
            'type': 'tree',
            'views': [(res_id, 'tree'), (res_id_form, 'form')],
            'target': 'current',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        if appoinment_id_list:
            result['domain'] = "[('id','in',%s)]" % appoinment_id_list
        return result
