# -*- coding: utf-8 -*-

from odoo import fields, models

class SoCancelReasonCustom(models.Model):
    _name = "so.cancel.reason.custom"
    _description = 'Cancel Reason'
    
    name = fields.Char(
        string='Name',
        required=True,
    )