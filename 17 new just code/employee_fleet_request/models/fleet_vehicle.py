# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'


    #@api.multi
    def action_view_request(self):
        self.ensure_one()
        #action = self.env.ref('employee_fleet_request.fleet_employee_request_action').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('employee_fleet_request.fleet_employee_request_action')
        action['domain'] = str([('vehicle_id', 'in', self.ids)])
        return action

class HrEmployee(models.Model):
    _inherit = "hr.employee"


    #@api.multi
    def action_view_employee(self):
        self.ensure_one()
        #action = self.env.ref('employee_fleet_request.fleet_employee_request_action').sudo().read()[0]
        action = self.env['ir.actions.act_window']._for_xml_id('employee_fleet_request.fleet_employee_request_action')
        action['domain'] = str([('employee_id', 'in', self.ids)])
        return action
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
