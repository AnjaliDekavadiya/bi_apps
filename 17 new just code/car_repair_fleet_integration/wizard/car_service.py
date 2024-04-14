# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CarServiceWizard(models.TransientModel):
    _name = 'car.service.wizard'
    _description = 'Car Service Wizard'
    
    service_type_ids = fields.Many2many(
        'fleet.service.type',
        string='Service Type',
    )
    
    @api.model
    def default_get(self, fields):
        rec = super(CarServiceWizard, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_id = context.get('active_ids')
        car_repair_support_id = self.env[active_model].browse(active_id)
        fleet_service_type_ids = car_repair_support_id.repair_types_ids.mapped('fleet_service_type_ids')
        vals = []
        for line in fleet_service_type_ids:
            vals.append((0,0,{'name': line.name ,
                              'category':line.category}))
        rec.update({'service_type_ids': vals})
        return rec
    
    #@api.multi
    def create_vehicle_services(self):
        context = dict(self._context or {})
        fleet_service_list = []
        active_model = context.get('active_model')
        active_id = context.get('active_ids')
        repair_support = self.env[active_model].browse(active_id)
        if self.service_type_ids:
            for service in self.service_type_ids:
                vals = {
                    'vehicle_id' : repair_support.vehicle_id.id,
                    # 'cost_subtype_id' : service.id,
                    'service_type_id' : service.id,
                    'car_repair_support_id' : repair_support.id,
                }
                fleet_vehicle_log_service_id = self.env['fleet.vehicle.log.services'].create(vals)
                fleet_service_list.append(fleet_vehicle_log_service_id.id)
        # action = self.env.ref("fleet.fleet_vehicle_log_services_action").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('fleet.fleet_vehicle_log_services_action')
        action['domain'] = [('id', 'in', fleet_service_list)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
