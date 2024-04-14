# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    level_config_id = fields.Many2one(
        'helpdesk.level.config',
        string="HelpDesk SLA Level Config",
    )
