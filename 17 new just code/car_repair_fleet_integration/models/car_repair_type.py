# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CarRepairtype(models.Model):
    _inherit = 'car.repair.type'

    fleet_service_type_ids = fields.Many2many(
        'fleet.service.type',
        string='Currency',
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
