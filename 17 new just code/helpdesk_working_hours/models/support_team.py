# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class SupportTeam(models.Model):

    _inherit = 'support.team'

    custom_support_team_id = fields.Many2one(
        'resource.calendar',
        string='Working Hours',
    )
    custom_is_default = fields.Boolean(
        'Is Default Working Hours?',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
