# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields , api

class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    custom_car_repair_id = fields.Many2one(
        'car.repair.support',
        string='Car Repair',
        readonly=True,
        copy=False
    )

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
