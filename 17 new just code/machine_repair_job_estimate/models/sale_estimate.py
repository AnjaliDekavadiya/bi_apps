# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleEstimate(models.Model):
    _inherit = "sale.estimate"
    
    machine_repair_support_id = fields.Many2one(
        "machine.repair.support",
        string="Machine Repair Request",
        copy=False,
    )
    
    #@api.multi
    def show_machine_repair(self):
        self.ensure_one()
        #action = self.env.ref("machine_repair_management.action_machine_repair_support").sudo().read()[0]
        action = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_machine_repair_support")
        action["domain"] = [('id', '=', self.machine_repair_support_id.id)]
        return action
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
