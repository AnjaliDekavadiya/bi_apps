# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    laundry_ticket_id = fields.Many2one(
        'laundry.business.service.custom',
        string='Laundry Request',
        readonly=True,
        copy=False,
    )