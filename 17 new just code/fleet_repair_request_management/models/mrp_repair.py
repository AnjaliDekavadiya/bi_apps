# -*- coding: utf-8 -*-

from odoo import fields, models

class Repair(models.Model):
    _inherit = 'repair.order'
    
    custom_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        copy=False,
        readonly=True,
    )
    custom_fleet_repair_id = fields.Many2one(
        'fleet.request',
        string='Repair Reference',
        readonly=True,
        copy=False,
    )
   