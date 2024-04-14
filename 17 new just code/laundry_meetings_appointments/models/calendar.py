# -*- coding: utf-8 -*-

from odoo import models, fields


class CalendarEvent(models.Model):
    _inherit = "calendar.event"
    
    meeting_custom_type = fields.Selection(
        [('collection_type','Appointment for Collection'),
        ('delivery_type','Appointment for Delivery')],
        string='Laundry Appointment Type',
        required=False,
        copy=True,
    )
    laundry_request_custom_id = fields.Many2one(
        'laundry.business.service.custom',
        string='Laundry Request',
        readonly=False,
        copy=False,
    )
