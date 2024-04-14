# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    custom_partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )

    custom_repair_count = fields.Integer(
        compute='_compute_repair_counter',
        string="Machine Repair",
    )

    def _compute_repair_counter(self):
        for rec in self: rec.custom_repair_count = self.env['machine.repair.support'].search_count([('custom_equipment_id', 'in', rec.ids)])

    #@api.multi
    def action_machine_repair(self):
        self.ensure_one()
        # for rec in self:
        #     action = self.env.ref('machine_repair_management.action_machine_repair_support').sudo().read()[0]
        action = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_machine_repair_support")
        action['domain'] = [('custom_equipment_id', '=', self.id)]
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
