# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rma_order_id = fields.Many2one(
        'return.order',
        string = "RMA Order"
    )
