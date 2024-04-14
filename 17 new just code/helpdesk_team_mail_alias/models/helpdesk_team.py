# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SupportTeam(models.Model):
    _name = 'support.team'
    _inherit = ['mail.alias.mixin', 'support.team']

    alias_id = fields.Many2one(
        'mail.alias',
        string='Alias',
        ondelete="restrict",
        # required=False,
        required=True, #odoo13
        help="The email address associated with this channel.New emails received will automatically create new leads assigned to the channel."
    )

    # def get_alias_values(self):
    #     values = super(SupportTeam, self).get_alias_values()
    #     values['alias_defaults'] = {
    #         'team_id': self.id,
    #     }
    #     return values

    # def get_alias_model_name(self, vals):
    #     return 'helpdesk.support'
    
    def _alias_get_creation_values(self):
        values = super(SupportTeam, self)._alias_get_creation_values()
        values['alias_defaults'] = {
                'team_id': self.id,
            }
        values['alias_model_id'] = self.env['ir.model']._get('helpdesk.support').id
        return values