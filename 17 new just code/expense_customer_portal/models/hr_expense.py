# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrExpense(models.Model):
    _inherit = "hr.expense"

    custom_partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        copy=False,
    )