# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    custom_tailor_request_id = fields.Many2one(
        'cloth.request.details',
        string="Tailor Request"
    )