# -*- coding: utf-8 -*-

from odoo import fields, models


class CarRepairInspectionRecord(models.Model):
    _name = "car.repair.inspection.record"
    _description = 'Car Repair Inspection Record'

    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
