# -*- coding: utf-8 -*-

from odoo import models, fields

class Partner(models.Model):
    _inherit = 'res.partner'
    
    is_available_for_apointment = fields.Boolean(
        'Available for Appointment / Schedule?',
        copy=False,
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
