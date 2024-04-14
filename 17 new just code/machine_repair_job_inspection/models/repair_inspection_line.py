# -*- coding: utf-8 -*-

from odoo import fields, models


class RepairOrderInspectionLine(models.Model):
    _name = "repair.order.inspection.line"
    _description = 'Repair Order Inspection Line'

    repair_inspection_id = fields.Many2one(
        'repair.order.inspection',
        string="Repair Inspection"
    )
    inspection_record = fields.Many2one(
        'repair.inspection.record',
        string="Inspection",
        required=True,
    )
    inspection_result = fields.Many2one(
        'repair.inspection.result',
        string="Inspection Result",
        required=True,
    )
    description = fields.Char(
        string="Description",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
