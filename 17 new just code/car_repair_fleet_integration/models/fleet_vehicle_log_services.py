# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    car_repair_support_id = fields.Many2one(
        'car.repair.support',
        string='Car Repair Reference',
        copy=False,
    )
    
    custom_ticket_count = fields.Integer(
        string='# of Ticket',
        compute='_compute_ticket_count', 
        readonly=True, 
        default=0,
        copy=False,
        store=True,
    )
    
    @api.depends()
    def _compute_ticket_count(self):
        repair_support = self.env['car.repair.support']
        for record in self:
            record.custom_ticket_count = repair_support.search_count([('id', '=', record.car_repair_support_id.id)])
            
    #@api.multi
    def show_car_ticket(self):
        self.ensure_one()
        # action = self.env.ref("car_repair_maintenance_service.action_car_repair_support").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('car_repair_maintenance_service.action_car_repair_support')
        action['domain'] = [('id', '=', self.car_repair_support_id.id)]
        return action
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
