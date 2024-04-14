# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def custom_action_view_cloth_requests(self):
        self.ensure_one()
        # action = self.env.ref('cloth_tailor_management_odoo.action_cloth_request_details').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('cloth_tailor_management_odoo.action_cloth_request_details')
        action['context'] = {}
        cloth_request_ids = self.env['cloth.request.details'].search([('custom_bom_id', 'in', self.ids)])
        action['domain'] = [('id', 'in', cloth_request_ids.ids)]
        return action