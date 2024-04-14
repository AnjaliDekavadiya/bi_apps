 # -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields,api
from datetime import datetime, timedelta,date

class InspectionRequest(models.Model):
    _name = 'inspection.request'
    _description = 'Inspection Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle",
        required=True
    )
    model_id = fields.Many2one(
        'fleet.vehicle.model', 
        'Model',
        required=True
    )
    custom_license_plate = fields.Char(
        string="License Plate"
    )
    inspection_line_id = fields.Many2one(
        'vehicle.inspection.line',
        string='Inspection Line',
    )
    note = fields.Text(
        string="Description"
    )
    state = fields.Selection(
        [('draft','New'),
         ('in_progress','Inspection Started'),
         ('inspection_done','Inspection Finished'),
         ('cancel','Cancelled')
         ],
        string='State',
        default='draft',
        copy=False,
        track_visibility="onchange" 
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Inspection Supervisor', 
        required=True, 
    )
    create_date = fields.Date(
        string="Create Date"
    )
    image = fields.Binary(
        #related='vehicle_id.image', 
        related='vehicle_id.image_128',
        string="Logo", 
        readonly=False,
    )
    name = fields.Char(
        string='Inspection Request'
    )
    next_date = fields.Date(
        string="Inspection Date"
    )
    inspection_request = fields.Text(
        string="Inspection Result"
    )
    image1 = fields.Binary(
        string="Image 1", 
        readonly=False,
    )
    image2 = fields.Binary(
        string="Image 2",
        readonly=False,
    )
    image3 = fields.Binary(
        string="Image 3",
        readonly=False,
    )
    image4 = fields.Binary(
        string="Image 4",
        readonly=False,
    )
    image5 = fields.Binary(
        string="Image 5",
        readonly=False,
    )
    inspection_request_title = fields.Char(
        string="Request For",
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.user.company_id
    )
    is_service = fields.Boolean(
        string="Is Service"
    )

    @api.model
    def _prepare_inspection_request(self,line):
        vals = {
            'vehicle_id':line.vehicle_id.id,
            'model_id':line.vehicle_id.model_id.id,
            'inspection_line_id':line.id,
            'custom_license_plate':line.vehicle_id.license_plate,
            'note':line.note,
            'user_id':line.user_id.id,
            'create_date':line.last_inspection_date,
            'next_date':line.last_inspection_date,
            'inspection_request_title':line.note,
        }
        return vals

    @api.model
    def _run_inspect_request_cron(self):
        inspection_lines = self.env['vehicle.inspection.line'].search([])
        for lines in inspection_lines:
            prives_date = lines.next_inspection_date - timedelta(days=lines.date_reminder)
            if prives_date == fields.date.today():
                vals=self._prepare_inspection_request(lines)
                inspection_request_id = self.env['inspection.request'].create(vals)
                mail_template_id = self.env.ref('fleet_safety_inspection.fleet_inspection_saftey_email_templte')
                mail_template_id.send_mail(inspection_request_id.id)
            period = lines.vehicle_inspection.period 
            last_inspection_date = date.today()
            next_inspection_date = last_inspection_date+timedelta(days=int(period))
            lines.last_inspection_date = last_inspection_date
            lines.next_inspection_date = next_inspection_date
            
            
            
    #@api.multi
    def action_reset_draft(self):
        return self.write({'state': 'draft'})

    #@api.multi
    def action_inspect_start(self):
        return self.write({'state': 'in_progress'})

    #@api.multi
    def action_inspect_done(self):
        return self.write({'state': 'inspection_done'})

    #@api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('inspection.request')
        return super(InspectionRequest, self).create(vals)

    #@api.multi
    def action_open_service(self):
        self.ensure_one()
        action = self.env.ref('fleet.fleet_vehicle_log_services_action').sudo().read()[0]
        action['domain'] = [('inspection_id', '=', self.id)]
        return action

    #@api.multi
    def action_open_vehicle(self):
        self.ensure_one()
        action = self.env.ref('fleet.fleet_vehicle_action').sudo().read()[0]
        action['domain'] = [('id', '=', self.vehicle_id.id)]
        return action

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        for rec in self:
            rec.model_id = rec.vehicle_id.model_id.id
            rec.custom_license_plate = rec.vehicle_id.license_plate
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
