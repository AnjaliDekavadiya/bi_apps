# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class JObCost(models.Model):
    _inherit = "job.costing"
    
    laundry_request_id = fields.Many2one(
        'laundry.business.service.custom',
        string="Laundry Request",
        copy=False,
        readonly=False
    )

class JobCostLine(models.Model):
    _inherit = "job.cost.line"
    
    laundry_job_cost_line = fields.Many2one(
        'laundry.jobcost.line',
        string="Laundry JobCost Line",
        copy=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
