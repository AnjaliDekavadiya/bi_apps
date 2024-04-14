# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class ClothRequestDetails(models.Model):
    _inherit = 'cloth.request.details'

    probc_is_repair_stage = fields.Boolean(
        string="Is Repair Stage",
        related='stage_id.probc_is_repair_stage',
        store=True
    )

    def custom_action_repair_request(self):
        self.ensure_one()
        # action = self.env.ref('repair.action_repair_order_tree').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('repair.action_repair_order_tree')
        action['context'] = {}
        repair_ids = self.env['repair.order'].search([('cloth_request_id', 'in', self.ids)])
        action['domain'] = [('id', 'in', repair_ids.ids)]
        return action