# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt.
# Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MachineRepairSupport(models.Model):
    _inherit = "machine.repair.support"

    custom_equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Equipment',
        copy=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
