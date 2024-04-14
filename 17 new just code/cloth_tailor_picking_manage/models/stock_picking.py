# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    custom_tailor_request_id = fields.Many2one(
        'cloth.request.details',
        string="Tailor Request"
    )