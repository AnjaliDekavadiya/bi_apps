# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class ResUers(models.Model):
    _inherit = 'res.users'

    cloth_team_id = fields.Many2one(
        'tailor.team',
        string='Tailor Team',
        copy=False
    )