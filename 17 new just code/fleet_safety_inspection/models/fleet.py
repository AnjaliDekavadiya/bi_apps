 # -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields,api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    inspection_line_ids = fields.One2many(
        'vehicle.inspection.line',
        'vehicle_id',
        string="Vehicle Inspection Line",
    )

    #@api.multi
    def action_open_vehicle_configration(self):
        self.ensure_one()
        action = self.env.ref('fleet_safety_inspection.action_vehicle_request_view').sudo().read()[0]
        action['domain'] = [('vehicle_id', '=', self.id)]
        return action
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: