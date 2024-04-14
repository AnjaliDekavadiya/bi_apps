 # -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _

class CreateService(models.TransientModel):
    _name = "create.service"
    _description= 'Create Service'

    cost_subtype_id = fields.Many2one(
        'fleet.service.type', 
        string='Type',
        required=True
    )
    service_id = fields.Many2one(
        'fleet.vehicle.log.services',
        string='Service',
        required=True
    )
    odometer = fields.Float(
        string='Odometer',
        required=True
    )
    odometer_unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('miles', 'Miles')
        ], 'Odometer Unit', default='kilometers',
        required=True
    )
    custom_cost_subtype_id = fields.Many2many(
        'fleet.service.type', 
        string="Sub Type",
        required=True
    )

    #@api.multi
    def action_create_service(self):
        active_ids = self._context.get('active_ids')
        inspection_id = self.env['inspection.request'].browse(self._context.get('active_ids'))
        for rec in self:
            lines = []
            for service in rec.custom_cost_subtype_id:
                lines.append((0,0,{'cost_subtype_id': service.id,
                              }))
            service_id = self.env['fleet.vehicle.log.services'].create({
                    # 'cost_subtype_id':rec.cost_subtype_id.id,
                    #'service_id':inspection_id.id,
                    'odometer':rec.odometer,
                    'odometer_unit':rec.odometer_unit,
                    'vehicle_id':inspection_id.vehicle_id.id,
                    'inspection_request':inspection_id.inspection_request,
                    'inspection_id':inspection_id.id,
                    'image1':inspection_id.image1,
                    'image2':inspection_id.image2,
                    'image3':inspection_id.image3,
                    'image4':inspection_id.image4,
                    'image5':inspection_id.image5,
                    # 'cost_ids':lines,
                })
            inspection_id.is_service = True
        action = self.env.ref('fleet.fleet_vehicle_log_services_action').sudo().read()[0]
        action['domain'] = str([('id', '=', service_id.id)])
        return action
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
