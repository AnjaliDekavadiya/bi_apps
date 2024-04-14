# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class JObCost(models.Model):
    _inherit = "job.costing"
    
    cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string="Cloth Request",
        copy=True
    )

class JobCostLine(models.Model):
    _inherit = "job.cost.line"
    
    cloth_job_cost_line = fields.Many2one(
        'cloth.jobcost.line',
        string="Cloth JobCost Line",
        copy=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
