# -*- coding: utf-8 -*-

from odoo import models, fields

class FleetTeam(models.Model):
    _name = 'fleet.team'
    _rec_name = 'name'
    _description = 'Fleet Repair Team'
    
    name = fields.Char(
        string='Name',
        required=True,
    )
    team_ids = fields.Many2many(
        'res.users',
        string='Team Members'
    )
    is_team = fields.Boolean(
        'Is Default Team?',
        help='Tick this box to set this team as default repair team when request come from website.',
    )
    leader_id = fields.Many2one(
        'res.users',
        string='Leader',
        required=True,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
