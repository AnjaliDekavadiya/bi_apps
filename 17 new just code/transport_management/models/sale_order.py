# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    """Sale Order"""
    _inherit = 'sale.order'
    _description = __doc__

    shipment_id = fields.Many2one('transport.shipment', string="Shipment Order")
    shipment_count = fields.Integer(compute="_get_shipment_count")

    def _get_shipment_count(self):
        shipment_order = self.env['transport.shipment'].sudo()
        for record in self:
            record.shipment_count = shipment_order.search_count([('id', '=', record.shipment_id.id)])

    def get_shipments(self):
        self.ensure_one()
        domain = [('id', '=', self.shipment_id.id)]
        return {
            'name': _('Shipment Orders'),
            'res_model': 'transport.shipment',
            'domain': domain,
            'type': 'ir.actions.act_window',
            'views': [(False, 'kanban'), (False, 'tree'), (False, 'form')],
            'view_mode': 'kanban'
        }

    def action_create_shipping(self):
        ship_order_view = self.env.ref('transport_management.ship_order_wizard_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'ship.order',
            'view_id': ship_order_view,
            'target': 'new',
            'context': {
                'active_ids': self.ids,
            },
        }
