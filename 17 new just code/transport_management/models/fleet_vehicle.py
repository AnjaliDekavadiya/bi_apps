# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import models, fields, api, _


class FleetVehicle(models.Model):
    """Fleet Vehicle"""
    _inherit = 'fleet.vehicle'
    _description = __doc__

    transporter_id = fields.Many2one('transporter.details', string="Transporter")


class ResPartner(models.Model):
    """Res Partner"""
    _inherit = 'res.partner'
    _description = __doc__

    is_driver = fields.Boolean(string="Driver")
    is_transporter = fields.Boolean(string="Transporter")

    driver_license = fields.Char(string="License ID")
    license_type = fields.Char()
    days_to_expire = fields.Integer(compute='_compute_days_to_expire')
    license_valid_from = fields.Date()
    license_expiration = fields.Date()

    @api.depends('license_expiration')
    def _compute_days_to_expire(self):
        for rec in self:
            date = fields.Date.context_today(self)
            if rec.license_expiration:
                date = rec.license_expiration
            now = fields.Date.context_today(self)
            delta = date - now
            rec.days_to_expire = delta.days if delta.days > 0 else 0
