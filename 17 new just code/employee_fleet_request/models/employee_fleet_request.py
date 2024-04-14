# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class VehicleFeeltRequest(models.Model):
    _name = 'vehicle.fleet.request'
    _description = 'Vehicle Feelt Request'
    _inherit = ['mail.thread']


    def _default_employee(self):
       return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one(
        'hr.employee', 
        string="Employee", 
        required=True,
        default=_default_employee
    )
    department_id = fields.Many2one(
        'hr.department', 
        string="Department",
        required=False 
    )
    request_date = fields.Date(
        string="Request Date",
        required=True,
        default=fields.Date.today()
    )
    custom_model_id = fields.Many2one(
        'fleet.vehicle.model', 
        'Model',
        required=False
    )
    note = fields.Text(
        string="Description"
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Request To', 
        required=True, 
    )
    state = fields.Selection(
        [('a_draft','New'),
         ('b_confirm','Confirmed'),
         ('c_approve','Approved'),
         ('d_assign','Assigned'),
         ('return','Returned'),
         ('reject','Reject'),
         ('cancel','Cancelled')],
        string='State',
        default='a_draft',
        copy=False,
        # track_visibility="onchange" 
        tracking=True,
    )
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle",
    )
    custom_license_plate = fields.Char(
        string="License Plate"
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        required=True,
        default=lambda self: self.env.user.company_id,
        readonly=True
    )
    start_date = fields.Datetime(
        string='Start Date'
    )
    end_date = fields.Datetime(
        string="End Date"
    )
    return_date = fields.Date(
        string="Returned Date",
        readonly=True,
        copy=False
    )
    request_title = fields.Char(
        string="Request For",
        required=True
    )
    request_reson = fields.Text(
        string="Vehicle Request Reason"
    )
    
    custom_task_id = fields.Many2one(
        'project.task', 
        string="Task", 
    )
    project_id = fields.Many2one(
        'project.project', 
        string="Project",
    )
    custom_user_id = fields.Many2one(
        'res.users', 
        string='Created By',
        default=lambda self: self.env.user ,
        required=True,
    )
    name = fields.Char(
        string='Number'
    )
    image = fields.Binary(
        #related='vehicle_id.image',
        related='vehicle_id.image_128',
        string="Logo", 
        readonly=False,
        store=True,
    )
    image_small = fields.Binary(
        string="Logo (small)", 
        readonly=False,
        store=True
    )
    confirm_by = fields.Many2one(
        'res.users',
        string="Confirmed By",
        readonly=True,
        copy=False
    )
    confirm_date = fields.Date(
        string="Confirmed Date",
        readonly=True,
        copy=False
    )
    assign_date = fields.Date(
        string="Assigned Date",
        readonly=True,
        copy=False
    )
    assign_by = fields.Many2one(
        'res.users',
        string="Assigned By",
        readonly=True,
        copy=False
    )
    approve_date = fields.Date(
        string="Approved Date",
        readonly=True,
        copy=False
    )
    approve_by = fields.Many2one(
        'res.users',
        string="Approved By",
        readonly=True,
        copy=False
    )
    return_by = fields.Many2one(
        'res.users',
        string="Returned By",
        readonly=True,
        copy=False
    )
    # vehicle_name = fields.Text(
    #     string="Vehicle"
    # )
    

    #@api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    #@api.multi
    def action_reset_draft(self):
        for rec in self:
            rec.assign_date = False
            rec.return_date = False
        return self.write({'state': 'a_draft'})

    #@api.multi
    def action_confirm(self):
        for rec in self:
            rec.confirm_date = fields.date.today()
            rec.confirm_by = rec.env.uid

            rec.write({'state': 'b_confirm'})

    #@api.multi
    def action_return(self):
        for rec in self:
            rec.return_date = fields.date.today()
            rec.return_by = rec.env.uid
            rec.write({'state': 'return'})

    #@api.multi
    def action_assign(self):
        for rec in self:
            rec.assign_date = fields.date.today()
            rec.assign_by = rec.env.uid
            rec.write({'state': 'd_assign'})

    #@api.multi
    def action_approve(self):
        for rec in self:
            rec.approve_date = fields.date.today()
            rec.approve_by = rec.env.uid
            if not rec.vehicle_id or not rec.custom_model_id:
                raise UserError(_('You can not Approve Request without Selected Vehicle and Model.'))
            domain = [
                ('company_id','=',rec.company_id.id),
                '|',
                ('state','=','d_assign'),
                ('state','=','c_approve'),
               '|',
               ('start_date', '<=', rec.start_date) ,
               ('end_date', '>=', rec.start_date) ,
               '|',
               ('start_date', '<=', rec.end_date),
               ('end_date', '>=', rec.end_date),
           ]
            vehicle_request_id =self.env['vehicle.fleet.request'].search(domain)
            if len(vehicle_request_id) > 1:
                 raise UserError(_('You can not approve booking of vehicle in selected periods since it is booked by other employee.Please select other period and try.You may contact your manager.'))
            rec.write({'state': 'c_approve'})

    #@api.multi
    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    @api.onchange('employee_id')
    def _onchange_employee(self):
        for rec in self:
            rec.department_id = rec.employee_id.department_id.id
            rec.custom_user_id = rec.employee_id.user_id

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        for rec in self:
            rec.custom_model_id = rec.vehicle_id.model_id.id
            rec.custom_license_plate = rec.vehicle_id.license_plate

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            return {'domain': {'custom_task_id': [('project_id', '=', self.project_id.ids)]}}
        else:
            return {'domain': {'custom_task_id': []}}
               


    #@api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('a_draft', 'cancel'):
                raise UserError(_('You cannot delete Vehicle Request in this state.'))
        return super(VehicleFeeltRequest, self).unlink()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.fleet.request')
        return super(VehicleFeeltRequest, self).create(vals)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    

