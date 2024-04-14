# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class Partner(models.Model):
    
    _inherit = 'res.partner'
    
    request_count = fields.Integer(
        string='# of Machine Repair',
        compute='_compute_request_count', 
        readonly=True, 
        default=0
    )
    
    @api.depends()
    def _compute_request_count(self):
        repair_support = self.env['machine.repair.support']
        for record in self:
            record.request_count = repair_support.search_count([('partner_id', 'child_of', record.id)])

#    @api.multi odoo13
    def open_repair_request(self):
        self.ensure_one()
        # action = self.env.ref('machine_repair_management.action_machine_repair_support').sudo().read()[0]
        action = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_machine_repair_support")
        action['domain'] = [('partner_id', 'child_of', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:



            
    
