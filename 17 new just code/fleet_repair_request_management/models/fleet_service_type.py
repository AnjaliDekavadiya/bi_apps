# -*- coding: utf-8 -*-

from odoo import fields, models


class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'
    
    service_charges = fields.Float(
        string='Charges',
        copy=False,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default= lambda self: self.env.user.company_id.currency_id.id,
        string='Currency', 
    )
    service_time = fields.Float(
        string='Service Time',
    )
