# -*- coding: utf-8 -*-

from odoo import fields, models


class RepairInspectionType(models.Model):
    _name = "repair.inspection.type"
    _description = 'Repair Inspection Type'

    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
