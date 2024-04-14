# -*- coding: utf-8 -*-

from odoo import models, fields , api


class MaterialPurchaseRequisition(models.Model):
    _inherit = "material.purchase.requisition"

    custom_fleet_request_id = fields.Many2one(
        'fleet.request',
        string='Fleet Repair Request',
        readonly=True,
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
