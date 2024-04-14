# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def action_view_pos_return_rma_custom(self):
        self.ensure_one()
        # action = self.env.ref('website_request_return_rma_odoo.action_return_repair_rma')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_request_return_rma_odoo.action_return_repair_rma')
        result['domain'] = [('posorder_id', 'in', self.ids)]
        return result