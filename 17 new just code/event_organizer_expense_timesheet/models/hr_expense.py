# -*- coding: utf-8 -*-

from odoo import fields, models

class HrExpense(models.Model):
    _inherit = "hr.expense"

    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False,
    )

    