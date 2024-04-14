 # -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    image1 = fields.Binary(
        string="Image1", 
        readonly=False,
    )
    image2 = fields.Binary(
        string="Image2",
        readonly=False,
    )
    image3 = fields.Binary(
        string="Image3",
        readonly=False,
    )
    image4 = fields.Binary(
        string="Image4",
        readonly=False,
    )
    image5 = fields.Binary(
        string="Image5",
        readonly=False,
    )
    inspection_request = fields.Text(
        string="Inspection Result"
    )
    inspection_id = fields.Many2one(
        'inspection.request',
        string='Inspection Request',
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
