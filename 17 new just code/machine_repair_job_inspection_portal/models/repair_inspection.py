# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RepairOrderInspection(models.Model):
    _inherit = 'repair.order.inspection'

    custom_inspector_ids = fields.Many2many(
        'res.partner',
        string="Share on Portal",
        copy=True
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
