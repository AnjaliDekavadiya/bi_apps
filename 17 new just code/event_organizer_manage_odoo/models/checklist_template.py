# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ChecklistTemplate(models.Model):
    _name = 'checklist.template.custom'
    _description = 'Checklist Template'

    name = fields.Char(
        string='Name',
        required=True,
    )
    checklist_ids = fields.Many2many(
        'event.checklist.custom',
        string='Checklists'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: