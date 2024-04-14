# -*- coding: utf-8 -*-

from odoo import fields, models


class RepairInspectionRecord(models.Model):
    _name = "repair.inspection.record"
    _description = 'Repair Inspection Record'

    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
