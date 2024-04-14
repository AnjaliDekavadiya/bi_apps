# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = "stock.move"

    fleet_repair_request_id = fields.Many2one(
        'fleet.request',
        string="Fleet Repair Request",
        domain=[('is_close','=',False)]
    )
    fleet_repaircustom_task_id = fields.Many2one(
        'project.task',
        string="Task"
    )

    @api.onchange('fleet_repair_request_id')
    def _onchange_fleet_repair(self):
        if self.fleet_repair_request_id:
            return {'domain': {'fleet_repaircustom_task_id': [('custom_fleet_id', '=', self.fleet_repair_request_id.ids)]}}
        else:
            return {'domain': {'fleet_repaircustom_task_id': []}}
