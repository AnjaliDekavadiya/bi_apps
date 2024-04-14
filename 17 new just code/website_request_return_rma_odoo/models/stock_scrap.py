# -*- coding: utf-8 -*-

from odoo import models, fields


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    rma_order_id = fields.Many2one(
        'return.order',
        string = "RMA Order"
    )
