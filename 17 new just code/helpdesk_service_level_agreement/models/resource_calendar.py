# -*- coding: utf-8 -*-

from odoo import models, fields


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    hours_per_week_probc = fields.Float(
        string="Hour per Week",
    )
    
    hours_per_day_probc = fields.Float(
        string="Hour per Day",
    )
    
    
