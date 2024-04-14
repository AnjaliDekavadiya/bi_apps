# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    custom_partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        store = True,
        related='equipment_id.custom_partner_id',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
