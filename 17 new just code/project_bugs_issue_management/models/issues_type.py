# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CustomIssuesType(models.Model):
    _name = 'custom.issues.type'

    name = fields.Char(
        required=True,
        string="Type Name"
    )
