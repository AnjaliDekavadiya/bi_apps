# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MachineRepair(models.Model):
    _inherit = 'machine.repair'

    machine_repair_orderline = fields.One2many('create.repair.request', 'new_order_line', string="Order Line")


class JobOrder(models.Model):
    _inherit = "job.order"

    repair_count = fields.Integer('Repair Request', compute='_get_repair_request')

    def _get_repair_request(self):
        for project in self:
            cost_ids = self.env['machine.repair'].search([('project_id', '=', self.project_id.id)])
            project.repair_count = len(cost_ids)

    def job_order_machine_button(self):
        self.ensure_one()
        return {
            'name': 'Machine Repair',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'machine.repair',
            'domain': [('project_id', '=', self.project_id.id)],
        }


class MachineDiagnosys(models.Model):
    _inherit = 'machine.diagnosys'

    def consume_car_parts(self):
        setting = self.env['res.config.settings'].search([], order="id desc", limit=1)

        if setting.consume_parts:
            picking_type_id = self.env['stock.picking.type'].search(
                [['code', '=', 'internal'], ['warehouse_id.company_id', '=', self.env.user.company_id.id]], limit=1)
            if not picking_type_id:
                warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)],
                                                               limit=1)

                picking_type_id = self.env['stock.picking.type'].create({
                    'name': 'Consume Parts',
                    'code': 'internal',
                    'sequence_id': self.env['ir.sequence'].search([['prefix', 'like', warehouse.code]], limit=1).id,
                    'sequence_code': 'IN',
                    'warehouse_id': warehouse.id or False,
                    'company_id': self.env.user.company_id.id,
                    'default_location_src_id': setting.location_id.id,
                    'default_location_dest_id': setting.location_dest_id.id,
                })

            picking = self.env['stock.picking'].create({
                'partner_id': self.assigned_to.partner_id.id,
                'picking_type_id': picking_type_id.id,
                'picking_type_code': 'internal',
                'location_id': setting.location_id.id,
                'location_dest_id': setting.location_dest_id.id,
                'origin': self.name,
            })
            for estitmate in self.machine_repair_estimation_ids:
                move = self.env['stock.move'].create({
                    'picking_id': picking.id,
                    'name': estitmate.product_id.name,
                    'product_uom': estitmate.product_id.uom_id.id,
                    'product_id': estitmate.product_id.id,
                    'product_uom_qty': estitmate.quantity,
                    'location_id': setting.location_id.id,
                    'location_dest_id': setting.location_dest_id.id,
                    'origin': self.name,
                })
        else:
            raise Warning(_("Please select the Consume Parts option in Inventory Settings to consume Machine Parts"))
