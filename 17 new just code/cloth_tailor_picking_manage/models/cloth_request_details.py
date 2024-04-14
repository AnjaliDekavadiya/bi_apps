# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class ClothRequestDetails(models.Model):
    _inherit = 'cloth.request.details'

    @api.model
    def _get_incoming_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)], limit=1)
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id', '=', False)], limit=1)
        return picking_type[:1]

    @api.model
    def _get_outgoing_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)], limit=1)
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('warehouse_id', '=', False)], limit=1)
        return picking_type[:1]

    def _get_destination_location(self):
        self.ensure_one()
        if self.partner_id:
            return self.partner_id.property_stock_customer.id
        return self.picking_type_id.default_location_dest_id.id

    def action_new_incoming_stock_picking(self):
        self.ensure_one()
        # action = self.env.ref("cloth_tailor_picking_manage.custom_stock_action_picking_new").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('cloth_tailor_picking_manage.custom_stock_action_picking_new')
        picking_type_id = self._get_incoming_picking_type(self.company_id.id)
        action['context'] = {
            'default_picking_type_id': picking_type_id.id,
            'default_partner_id': self.partner_id.id,
            'default_user_id': False,
            'default_date': self.request_date,
            'default_origin': self.name,
            'default_location_dest_id': self._get_destination_location(),
            'default_location_id': self.partner_id.property_stock_supplier.id,
            'default_company_id': self.company_id.id,
            'default_custom_tailor_request_id': self.id,
        }
        return action

    def action_new_outgoing_stock_picking(self):
        self.ensure_one()
        # action = self.env.ref("cloth_tailor_picking_manage.custom_stock_action_picking_new").sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('cloth_tailor_picking_manage.custom_stock_action_picking_new')
        picking_type_id = self._get_outgoing_picking_type(self.company_id.id)
        action['context'] = {
            'default_picking_type_id': picking_type_id.id,
            'default_partner_id': self.partner_id.id,
            'default_user_id': False,
            'default_date': self.request_date,
            'default_origin': self.name,
            'default_location_dest_id': self._get_destination_location(),
            'default_location_id': self.partner_id.property_stock_supplier.id,
            'default_company_id': self.company_id.id,
            'default_custom_tailor_request_id': self.id,
        }
        return action

    def custom_action_view_incoming_picking(self):
        self.ensure_one()
        # action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('stock.action_picking_tree_all')
        action['context'] = {}
        picking_ids = self.env['stock.picking'].search([
            ('custom_tailor_request_id', 'in', self.ids),
            ('picking_type_code', '=', 'incoming')
        ])
        action['domain'] = [('id', 'in', picking_ids.ids)]
        return action

    def custom_action_view_outgoing_picking(self):
        self.ensure_one()
        # action = self.env.ref('stock.action_picking_tree_all').sudo().read()[0]
        action = self.env['ir.actions.actions']._for_xml_id('stock.action_picking_tree_all')
        action['context'] = {}
        picking_ids = self.env['stock.picking'].search([
                ('custom_tailor_request_id', 'in', self.ids),
                ('picking_type_code', '=', 'outgoing')
            ])
        action['domain'] = [('id', 'in', picking_ids.ids)]
        return action