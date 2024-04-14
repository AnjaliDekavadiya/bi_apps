# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class JObCost(models.Model):
    _inherit = "job.costing"
    
    car_support_id = fields.Many2one(
        'car.repair.support',
        string="Car Support",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
