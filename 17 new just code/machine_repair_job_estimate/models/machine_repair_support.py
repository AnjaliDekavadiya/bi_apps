# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MachineRepairSupport(models.Model):
    _inherit = "machine.repair.support"
    
    count_repair_estimate = fields.Integer(
        string="Count Estimate",
        compute="_compute_notes_count",
        # readonly=True,
        # default=0,
    )

    @api.depends()
    def _compute_notes_count(self):
        for rec in self:
            estimate_count = self.env['sale.estimate'].search_count([('machine_repair_support_id', '=', rec.id)])
            rec.count_repair_estimate = estimate_count
            
    #@api.multi
    def show_repair_estimate(self):
        self.ensure_one()
        # action = self.env.ref("odoo_sale_estimates.action_estimate").sudo().read()[0]
        action = self.env["ir.actions.actions"]._for_xml_id("odoo_sale_estimates.action_estimate")
        action["domain"] = [('machine_repair_support_id' , '=' , self.id)]
        return action
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
