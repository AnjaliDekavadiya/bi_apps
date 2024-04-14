# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class VehicleRentalDashboard(models.Model):
    """Vehicle Rental Dashboard"""
    _name = "vehicle.rental.dashboard"
    _description = __doc__

    @api.model
    def get_vehicle_rental_dashboard(self):
        total_vehicle = self.env['fleet.vehicle'].sudo().search_count([])
        available_vehicle = self.env['fleet.vehicle'].sudo().search_count([('status', '=', 'available')])
        under_maintenance_vehicle = self.env['fleet.vehicle'].sudo().search_count([('status', '=', 'in_maintenance')])
        draft_vehicle = self.env['vehicle.contract'].sudo().search_count([])
        in_progress_vehicle = self.env['vehicle.contract'].sudo().search_count([('status', '=', 'b_in_progress')])
        return_contract = self.env['vehicle.contract'].sudo().search_count([('status', '=', 'c_return')])
        cancel_contract = self.env['vehicle.contract'].sudo().search_count([('status', '=', 'd_cancel')])

        data = {
            'total_vehicle': total_vehicle,
            'available_vehicle': available_vehicle,
            'under_maintenance_vehicle': under_maintenance_vehicle,
            'draft_vehicle': draft_vehicle,
            'in_progress_vehicle': in_progress_vehicle,
            'return_contract': return_contract,
            'cancel_contract': cancel_contract,
        }
        return data
