# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = "stock.move"

    car_repair_request_id = fields.Many2one(
        'car.repair.support',
        string="Car Repair Request",
        domain=[('is_close','=',False)]
    )
    car_repaircustom_task_id = fields.Many2one(
        'project.task',
        string="Job Order"
    )

    @api.onchange('car_repair_request_id')
    def _onchange_machine_repair(self):
        if self.car_repair_request_id:
            return {'domain': {'car_repaircustom_task_id': [('car_ticket_id', '=', self.car_repair_request_id.ids)]}}
        else:
            return {'domain': {'car_repaircustom_task_id': []}}
