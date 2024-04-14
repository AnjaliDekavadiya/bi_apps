# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
import logging
from odoo.http import request
_logger = logging.getLogger(__name__)


class InheritedJobOrder(models.Model):
    _inherit = 'job.order'

    digital_signature = fields.Binary(string='Signature')

    def create_work_history_details(self, job, task , project , timedetails):
        if project:
            task_object = self.env['project.task'].search([('id','=',task)])
            employee_object = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
            project_object = self.env['project.project'].search([('id','=',project)])
            job_object = self.env['job.order'].search([('id' , '=' , job) , ('project_id','=',project_object.id)])
            for dict_line in timedetails:
                product_dict  = dict_line.get('time_details')
                vals = {
                    'date' : datetime.now().today(),
                    'project_id' : project_object.id ,
                    'task_id' : task_object.id,
                    'employee_id' : employee_object.id,
                    'st_time':product_dict.get('last_start_time'),
                    'ed_time':product_dict.get('last_stop_time'),
                    'name' : 'this time sheet for job order',
                    'unit_amount' :product_dict.get('total_duration'),
                    'account_analytic_line_id':job_object.id
                }
                timesheet = job_object.timesheet_ids.create(vals)
            return timesheet.id
        else:
            task_object = self.env['project.task'].search([('id','=',task)])
            employee_object = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
            project_object = self.env['project.project'].search([('id','=',self.project_id.id)])
            job_object = self.env['job.order'].search([('id' , '=' , self.id) , ('project_id','=',project_object.id)])
            for dict_line in timedetails:
                product_dict  = dict_line.get('time_details')
                vals = {
                    'date' : datetime.now().today(),
                    'project_id' : project_object.id ,
                    'task_id' : task_object.id,
                    'employee_id' : employee_object.id,
                    'st_time':product_dict.get('last_start_time'),
                    'ed_time':product_dict.get('last_stop_time'),
                    'name' : 'this time sheet for job order',
                    'unit_amount' :product_dict.get('total_duration'),
                    'account_analytic_line_id':job_object.id
                }
                timesheet = job_object.timesheet_ids.create(vals)
            return timesheet.id

    @api.model_create_multi
    def create(self, vals_list):
        res = super(InheritedJobOrder, self).create(vals_list)
        for vals in vals_list:
            if vals.get('project_id'):
                project_object = vals['project_id']
                if vals.get('customer_id'):
                    user = vals['customer_id']
                elif vals.get('user_id'):
                    user = vals['user_id']
                    user = self.env['res.users'].browse(int(user)).partner_id.id
                else:
                    user = self.env.user.partner_id.id
                if project_object:
                    project_details = self.env['project.project'].browse(int(project_object))
                    partner = self.env['res.partner'].browse(user)
                    login = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id

                    lst = []
                    for i in project_details.message_partner_ids:
                        lst.append(i)
                    lst2 = []
                    if partner not in lst :
                        self.env['mail.followers'].create({
                            'res_model': 'project.project',
                            'res_id': project_details,
                            'partner_id':partner.id
                        })

                    for i in project_details.message_partner_ids:
                        lst2.append(i)
                    if login not in lst2:
                        self.env['mail.followers'].create({
                            'res_model': 'project.project',
                            'res_id': project_details,
                            'partner_id':login.id
                        })
        return res 

class Website(models.Model):
    _inherit = 'website'
  
    job_order_id = fields.Integer("job orders details")
    def get_joborder_list(self , job_data):
        print("kfldklf",self)
        job_ids=self.env['job.order'].sudo().browse(job_data)
        self.update({'job_order_id' : job_ids.id})
        return job_ids
