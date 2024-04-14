# -*- coding: utf-8 -*-

# from openerp import models, fields, api
from odoo import models, fields, api #odoo13


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    machine_repair_id = fields.Many2one(
        'machine.repair.support',
        string="Machine Repair Request"
    )

    # @api.multi #odoo13
    def show_machine_repair_ids(self):
        self.ensure_one()
        # res = self.env.ref('machine_repair_management.action_machine_repair_support')
        # res = res.sudo().read()[0]
        res = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_machine_repair_support")
        res['domain'] = str([('id', '=', self.machine_repair_id.id)])
        return res