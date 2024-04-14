# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EventChecklist(models.Model):
    _name = 'event.checklist.custom'
    _description = 'Event Checklist'
    _order = 'sequence'

    name = fields.Char(
        string='Name',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: