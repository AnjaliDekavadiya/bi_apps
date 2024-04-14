# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReturnOrder(models.Model):
    _inherit = 'return.order'

    saleorder_id = fields.Many2one(
        required = False,
    )
    posorder_id = fields.Many2one(
        'pos.order',
        string="POS Order",
        required = False,
        copy=False
    )
    is_pos_order = fields.Boolean(
        string='RMA for POS?'
    )

    def pos_action_stock_picking_custom(self):
       self.ensure_one()
       action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_ready')
       action['context'] = {}
       if self.posorder_id.picking_ids :
           action['domain'] = [('id', 'in', self.posorder_id.picking_ids.ids)]
       else:
           action['domain'] = [('id', 'in', self.posorder_id.session_id.picking_ids.ids)]
       return action
