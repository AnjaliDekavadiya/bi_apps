# -*- coding: utf-8 -*-

from odoo import models, fields

class TypeOfSubject(models.Model):
    _name = 'construction.type.of.subject'
    _description = 'Construction Subject Type'
    
    name = fields.Char(
        'Name',
        required=True,
    )
