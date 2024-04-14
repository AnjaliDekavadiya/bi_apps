# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FleetVehicleWizard(models.TransientModel):
    _name = 'fleet.vehicle.wizard'
    _description = 'Fleet Vehicle Wizard'
    
    fleet_vehicle_model_id = fields.Many2one(
        'fleet.vehicle.model',
        string='Model',
        required=True,
    )
    
    license_plate = fields.Char(
        string="License Plate",
        readonly=False,
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    
    #@api.multi
    def create_fleet_vehicle(self):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_id = context.get('active_ids')
        car_repair_support_id = self.env[active_model].browse(active_id)
        vals = {}
        for rec in self:
            vals = {
                'model_id' : rec.fleet_vehicle_model_id.id,
                'license_plate' : rec.license_plate,
                #'partner_id' : rec.partner_id.id,
                'color' : car_repair_support_id.color,
                'model_year' : car_repair_support_id.year,
                'custom_product_id' : car_repair_support_id.product_id.product_tmpl_id.id,
            }
        fleet_vehicle_id = self.env['fleet.vehicle'].create(vals)
        car_repair_support_id.write({
            'vehicle_id' : fleet_vehicle_id.id,
            'license_plate' : rec.license_plate})
        # action = self.env.ref("fleet.fleet_vehicle_action").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('fleet.fleet_vehicle_action')
        action['domain'] = [('id', '=', fleet_vehicle_id.id)]
        return action
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
