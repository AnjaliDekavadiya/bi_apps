# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = "stock.move"

    repair_request_id = fields.Many2one(
        'machine.repair.support',
        string="Machine Repair Request",
        domain=[('is_close','=',False)]
    )
    custom_task_id = fields.Many2one(
        'project.task',
        string="Job Order"
    )

    @api.onchange('repair_request_id')
    def _onchange_machine_repair(self):
        if self.repair_request_id:
            return {'domain': {'custom_task_id': [('machine_ticket_id', '=', self.repair_request_id.ids)]}}
        else:
            return {'domain': {'custom_task_id': []}}
