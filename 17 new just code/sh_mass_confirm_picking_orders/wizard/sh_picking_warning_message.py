# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class PickingWarningMessage(models.TransientModel):
    _name = 'picking.warning.message'
    _description = 'Picking Warning Message'

    message = fields.Text(string='Message', readonly=True)
    compute_message = fields.Text(string='Message', readonly=True)
    backorder_message = fields.Text(string='Message', readonly=True)
