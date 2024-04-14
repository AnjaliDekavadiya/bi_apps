# -*- coding: utf-8 -*-

from odoo import models, fields

class SupportTeam(models.Model):
    _inherit = 'support.team'
    
    team_logo = fields.Binary(
        string="Team Logo",
    )
    html_description = fields.Html(
        string="HTML Description"
    )