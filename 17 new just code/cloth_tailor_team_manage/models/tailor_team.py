# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class TailorTeam(models.Model):
    _name = 'tailor.team'
    _description = 'Tailor Team'

    name = fields.Char(
        string="Name",
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string="Team Leader"
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        required=True, 
        default=lambda self: self.env.company
    )
    member_ids = fields.One2many(
        'res.users', 
        'cloth_team_id', 
        string='Channel Members',
        domain=[('share', '=', False)],
        copy=True
    ) #Unused field
    custom_member_ids = fields.Many2many(
        'res.users',
        string='Channel Members',
        domain=[('share', '=', False)],
        copy=False
    )