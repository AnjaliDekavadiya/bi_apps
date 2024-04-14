# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class LaundryBusinessTeam(models.Model):
    _name = 'laundry.business.team'
    _rec_name = 'name'
    _description = 'Laundry Business Team'
    
    name = fields.Char(
        string='Team Name',
        required=True,
    )
    team_ids = fields.Many2many(
        'res.users',
        string='Team Members'
    )
    is_team = fields.Boolean(
        'Default for website request?',
        help='Tick this box to set this team as default support team when request come from website',
    )
    leader_id = fields.Many2one(
        'res.users',
        string='Team Supervisor',
        required=True,
    )
    
    
    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        if not user_id:
            user_id = self.env.uid
        team_id = None
        if 'default_team_id' in self.env.context:
            team_id = self.browse(self.env.context.get('default_team_id'))
        if not team_id or not team_id.exists():
            team_id = self.sudo().search(
                ['|', ('leader_id', '=', user_id), ('team_ids', '=', user_id)],
                limit=1)
        return team_id
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
