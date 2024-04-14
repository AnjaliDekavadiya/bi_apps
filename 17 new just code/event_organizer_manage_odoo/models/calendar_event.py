# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False
    )