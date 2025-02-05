# -*- coding: utf-8 -*-

from odoo import fields, models


class RepairInspectionResult(models.Model):
    _name = "repair.inspection.result"
    _description = 'Repair Inspection Result'
    _order= 'id desc'

    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
