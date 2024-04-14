# -*- coding: utf-8 -*-

from odoo import models, fields, api


class JObCost(models.Model):
    _inherit = "job.costing"
    
    fleet_request_id = fields.Many2one(
        'fleet.request',
        string="Fleet Request",
        copy=False,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
