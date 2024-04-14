# -*- coding: utf-8 -*-

from odoo import fields, models

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
#     fleet_repair_id = fields.Many2one(
#         'fleet.request',
#         string='Repair Reference',
#         readonly=True,
#         copy=False,
#     )
    custom_partner_id = fields.Many2one(
        'res.partner',
        string="Customer"
    )
    fleet_repair_ids = fields.One2many(
        'fleet.request',
        'vehicle_id',
        string='Repair Reference',
        readonly=True,
        copy=False,
    )
    custom_product_id = fields.Many2one(
        'product.product',
        string='Product Related',
        copy=False,
    )

class FleetVehicleLogService(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    fleet_repair_id = fields.Many2one(
        'fleet.request',
        string='Repair Reference',
        readonly=True,
        copy=False,
    )

