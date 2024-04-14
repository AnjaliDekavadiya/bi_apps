# -*- coding: utf-8 -*

from odoo import models, fields

class ReplacementReasonCustom(models.Model):
    _name = 'replacement.reason.custom'
    _description = "Replacement Reason"
    
    name = fields.Char(
        string='Name',
        required=True,
    )