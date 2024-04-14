# -*- coding: utf-8 -*-

from odoo import fields, models


class CarRepairOrderInspectionLine(models.Model):
    _name = "car.repair.order.inspection.line"
    _description = 'Car Repair Order Inspection Line'

    repair_inspection_id = fields.Many2one(
        'car.repair.order.inspection',
        string="Repair Inspection",
        copy=False,
    )
    inspection_record = fields.Many2one(
        'car.repair.inspection.record',
        string="Inspection",
        required=True,
    )
    inspection_result = fields.Many2one(
        'car.repair.inspection.result',
        string="Inspection Result",
        required=True,
    )
    description = fields.Char(
        string="Description",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
