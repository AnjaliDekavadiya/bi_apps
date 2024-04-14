# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ClothMeasurmentDetails(models.Model):
    _name = 'cloth.measurement.details'
    _description = 'Cloth Measurment Details'
    _rec_name = 'cloth_type_id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True
    )
    measurement_date = fields.Date(
        default=fields.Date.context_today,
        string="Date"
    )
    cloth_type_id = fields.Many2one(
        'cloth.type',
        string="Cloth Type",
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible",
        default=lambda self: self.env.user
    )
    company_id = fields.Many2one(
        'res.company',
        required=True, 
        default=lambda self: self.env.company,
        string="Company"
    )
    internal_note = fields.Text(
        'Add an internal note...',
    )
    measurement_ids = fields.One2many(
        'cloth.measurement.details.line',
        'cloth_measurement_id',
        string="Measurement Types"
    )

    def action_create_request_line(self):
        for rec in self:
            if rec.cloth_type_id and not rec.measurement_ids:
                for line in rec.cloth_type_id.measurement_ids:
                    new_line_id = self.env['cloth.measurement.details.line'].create({
                        'cloth_measurement_id': rec.id,
                        'uom_id': line.uom_id.id,
                        'cloth_measurement_type_id': line.id,
                    })

class ClothMeasurementDetailsLine(models.Model):
    _name = 'cloth.measurement.details.line'
    _description = 'Cloth Measurment Details Line'
    
    cloth_measurement_id = fields.Many2one(
        'cloth.measurement.details',
        string="Cloth Measurement"
    )
    cloth_measurement_type_id = fields.Many2one(
        'cloth.measurement.type',
        string="Measurement Type",
        #readonly=True
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string="Unit of Measure"
    )
    measurement = fields.Float(
        string="Measurement"
    )
    cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string="Cloth Request"
    )
    measurement_details_line_id = fields.Many2one(
        'cloth.measurement.details.line',
        string="Measurement Line"
    )

    def action_update_line_measurement(self):
        for rec in self:
            if rec.measurement_details_line_id:
                rec.measurement_details_line_id.measurement = rec.measurement
