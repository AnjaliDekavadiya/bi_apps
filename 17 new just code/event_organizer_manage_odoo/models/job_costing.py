# -*- coding: utf-8 -*-

from odoo import models, fields

class JobCosting(models.Model):
    _inherit = 'job.costing'
    
    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False,
    )