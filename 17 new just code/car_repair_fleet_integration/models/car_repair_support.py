# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CarRepairSupport(models.Model):
    _inherit = 'car.repair.support'
    
    
    license_plate = fields.Char(
        string="License Plate",
        copy=False,
    )
    
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        copy=False,
    )
    
    custom_services_count = fields.Integer(
        string='# of Services',
        compute='_compute_services_count', 
        readonly=True, 
        default=0,
        copy=False,
    )
    
    custom_vehicle_count = fields.Integer(
        string='# of Vehicle',
        compute='_compute_vehicle_count', 
        readonly=True, 
        default=0,
        copy=False,
    )
    
    @api.onchange('vehicle_id')
    def _onchnage_vehicle_id(self):
        for rec in self:
            if rec.vehicle_id:
                rec.license_plate = rec.vehicle_id.license_plate
            
    @api.depends()
    def _compute_services_count(self):
        fleet_vehicle_services = self.env['fleet.vehicle.log.services']
        for record in self:
            record.custom_services_count = fleet_vehicle_services.search_count([('car_repair_support_id', '=', record.id)])
            
    @api.depends()
    def _compute_vehicle_count(self):
        fleet_vehicle = self.env['fleet.vehicle']
        for record in self:
            record.custom_vehicle_count = fleet_vehicle.search_count([('id', '=', record.vehicle_id.id)])

    #@api.multi
    def show_vehicle_services(self):
        self.ensure_one()
        # action = self.env.ref("fleet.fleet_vehicle_log_services_action").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('fleet.fleet_vehicle_log_services_action')
        action['domain'] = [('car_repair_support_id', '=', self.id)]
        return action
        
    #@api.multi
    def show_created_vehicle(self):
        self.ensure_one()
        # action = self.env.ref("fleet.fleet_vehicle_action").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('fleet.fleet_vehicle_action')
        action['domain'] = [('id', '=', self.vehicle_id.id)]
        return action
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
