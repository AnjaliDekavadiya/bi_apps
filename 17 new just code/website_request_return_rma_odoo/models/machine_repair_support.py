# -*- coding: utf-8 -*-

from odoo import models, fields


class MachineRepairSupport(models.Model):
    _inherit = 'machine.repair.support'

    rma_order_id = fields.Many2one(
        'return.order',
        string = "RMA Order"
    )
    quantity = fields.Float(
        string='Quantity',
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Product Uom'
    )
    reason_id = fields.Many2one(
        'return.reason',
        string='Return Reason',
    )
