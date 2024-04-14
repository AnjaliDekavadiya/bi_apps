# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False,
    )