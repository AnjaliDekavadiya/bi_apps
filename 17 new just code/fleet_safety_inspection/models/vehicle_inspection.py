 # -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class VehicleInspection(models.Model):
    _name = 'vehicle.inspection'
    _description = 'Vehicle Inspection'
    
    name = fields.Char(
        string='Name',
        required=True,
        copy=False,
    )
    period = fields.Char(
        string='Period(Days)',
    )
    custom_date_reminder = fields.Integer(
        string="Reminder Notification(Days)"
    )
    custom_user_id = fields.Many2one(
        'res.users', 
        string='Inspection Supervisor', 
        required=True, 
    )
    # uom_id = fields.Many2one(
    #      'uom.uom',
    #     string='Unit of Measure'
    # )

class VehicleInspectionLine(models.Model):
    _name = 'vehicle.inspection.line'
    _description = 'note'
    _rec_name = 'note'

    vehicle_inspection = fields.Many2one(
        'vehicle.inspection',
        string='Vehicle Inspection',
        required=True
    )
    last_inspection_date = fields.Date(
        string="Last Inspection Date"
    )
    next_inspection_date = fields.Date(
        string="Next Inspection Date"
    )
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string="Vehicle"
    )
    note = fields.Text(
        string="Description",
        required=True
    )
    date_reminder = fields.Integer(
        string="Reminder Notification(Days)",
        related='vehicle_inspection.custom_date_reminder'
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Inspection Supervisor', 
        required=True,
        related='vehicle_inspection.custom_user_id'
    )
    custom_period = fields.Char(
        string='Period(Days)',
        related='vehicle_inspection.period'
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: