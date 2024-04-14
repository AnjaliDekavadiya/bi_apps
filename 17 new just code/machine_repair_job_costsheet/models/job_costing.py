# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class JObCost(models.Model):
    _inherit = "job.costing"
    
    machine_support_id = fields.Many2one(
        'machine.repair.support',
        string="Machine Support",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
