# -*- coding: utf-8 -*-

import time

from odoo import models, fields, api, _
# from odoo.exceptions import Warning, ValidationError
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class VehicleServiceWizard(models.TransientModel):
    _name = 'vehicle.service.wizard'
    _description = 'Vehicle Service Wizard'
    
    service_type_ids = fields.Many2many(
        'fleet.service.type',
        string='Service Type',
    )
    
    @api.model
    def default_get(self, fields):
        rec = super(VehicleServiceWizard, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        repair = self.env[active_model].browse(active_ids)
        vals = []
        for line in repair.service_type_ids:
            vals.append((0,0,{'name': line.name ,
                              'category':line.category}))
        rec.update({'service_type_ids': vals})
        return rec
    
#    @api.multi odoo13
    def create_vehicle_services(self):
        picking = self.env['fleet.request'].browse(self._context.get('active_ids', []))
        service_ids = []
        if not self.service_type_ids:
            raise UserError(_('Please Select The Vehicle Services.'))
        else:
            service_ids.append(self.id)
            for service in self.service_type_ids:
                vals = {
                    'vehicle_id' : picking.vehicle_id.id,
                    # 'cost_subtype_id' : service.id,
                    'service_type_id' : service.id,
                    'fleet_repair_id' : picking.id,
                }
                fleet_vehicle_service = self.env['fleet.vehicle.log.services'].create(vals)
                service_ids.append(fleet_vehicle_service.id)
        # action = self.env.ref('fleet.fleet_vehicle_log_services_action')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.actions']._for_xml_id('fleet.fleet_vehicle_log_services_action')
        result['domain'] = [('id', 'in', service_ids)]
        return result
        
    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
