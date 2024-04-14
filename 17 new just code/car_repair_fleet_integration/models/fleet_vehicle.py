# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def write(self, vals):
        res = super(FleetVehicle, self).write(vals)
        if vals.get('custom_product_id'):
            prod_id = self.env['product.product'].search([('product_tmpl_id','=', vals['custom_product_id'])])
            prod_id.write({
                'is_car': True
                })
        return res
    
    custom_ticket_count = fields.Integer(
        string='# of Ticket',
        compute='_compute_ticket_count', 
        readonly=True,
        default=0,
        copy=False,
    )
    
    @api.depends()
    def _compute_ticket_count(self):
        repair_support = self.env['car.repair.support']
        for record in self:
            record.custom_ticket_count = repair_support.search_count([('vehicle_id', '=', record.id)])
            
    #@api.multi
    def show_car_ticket(self):
        self.ensure_one()
        # action = self.env.ref("car_repair_maintenance_service.action_car_repair_support").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('car_repair_maintenance_service.action_car_repair_support')
        action['domain'] = [('vehicle_id', '=', self.id)]
        return action
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
