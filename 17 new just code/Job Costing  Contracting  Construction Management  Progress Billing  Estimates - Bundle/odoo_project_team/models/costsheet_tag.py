# -*- coding: utf-8 -*-

from odoo import models, fields

class CostsheetTag(models.Model):
    _name = 'costsheet.tag'
    _description = 'Costsheet Tag'
    
    name = fields.Char(
        string='Name',
        required=True,
        copy=False,
    )
    color = fields.Integer(
        string='Color Index'
    )