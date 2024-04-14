# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class CarProductConsumePart(models.Model):
    _inherit = "car.product.consume.part"
    
    job_type = fields.Selection(
        selection=[
            ('material','Material'),
            ('labour','Labour'),
            ('overhead','Overhead')
        ],
        string="Type",
        default="material",
        required=True,
    )
    job_type_id = fields.Many2one(
        'job.type',
        string="Job Type",
        domain="[('job_type','=','material')]",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
