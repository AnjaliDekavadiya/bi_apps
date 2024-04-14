# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    custom_cloth_request_ids = fields.Many2many(
        'cloth.request.details',
        string="Cloth Requests"
    )
