# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class ClothRequestDetails(models.Model):
    _inherit = 'cloth.request.details'

    tailor_team_id = fields.Many2one(
        'tailor.team',
        string="Team",
        copy=True
    )
    tailor_team_leader_id = fields.Many2one(
        'res.users',
        related='tailor_team_id.user_id',
        string="Team Leader"
    )