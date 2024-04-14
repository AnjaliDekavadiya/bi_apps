# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _

class MassConfirmPicking(models.TransientModel):
    _name = 'mass.confirm.picking'
    _description = 'Mass Confirm Picking'

    message = fields.Text(string='Message', readonly=True)
    picking_validate_process = fields.Selection([('full','Fully Available'),('partial','Partial Available'),('force','Force Available')],default='full',string='Picking Available',required=True)
    backorder = fields.Boolean(string='Is Backorder ?')

    @api.model
    def default_get(self, fields):
        res = super(MassConfirmPicking, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        picking_orders = self.env['stock.picking'].browse(active_ids)
        order_list = []
        for order in picking_orders:
            if order.state in ['done','cancel']:
                order_list.append(order.name)
        msg = ','.join(order_list)
        if len(order_list) > 0:
            res.update({
                'message': "Following Picking Orders are in Done/Cancelled State" + " " + msg,
                })
        return res

    def action_confirm_picking(self):
        if self.env.context.get('active_ids', False):
            done_picking = []
            not_done_picking = []
            msg = ""
            message = ""
            backorder_message = ""
            backorder = []
            if self.picking_validate_process == 'full':
                for picking in self.env['stock.picking'].search([('id', 'in', self.env.context.get('active_ids', False))]):
                    if picking.state in ['done','cancel']:
                        not_done_picking.append(picking.name)
                    else:
                        is_partial = False
                        for check_move in picking.move_ids_without_package:
                            if check_move.state in ['partially_available','confirmed']:
                                is_partial = True
                        if is_partial:
                            not_done_picking.append(picking.name)
                        else:
                            for move in picking.move_ids_without_package:
                                move.sudo().write({
                                    'quantity': move.product_uom_qty
                                })
                            if picking.state in ['draft']:
                                picking.action_confirm()
                            if picking.state in ['confirmed']:
                                picking.action_assign()
                            if picking.state in ['assigned']:
                                picking.button_validate()
                            if picking.state in ['done']:
                                done_picking.append(picking.name)
                            else:
                                not_done_picking.append(picking.name)
            elif self.picking_validate_process == 'partial':
                for picking in self.env['stock.picking'].search([('id', 'in', self.env.context.get('active_ids', False))]):
                    if picking.state in ['done','cancel']:
                        not_done_picking.append(picking.name)
                    else:
                        if self.backorder:
                            is_partial = False
                            for move in picking.move_ids_without_package:
                                if move.state in ['confirmed', 'partially_available','assigned']:
                                    is_partial = True
                                move.sudo().write({
                                    'quantity': move.forecast_availability,
                                })
                            if is_partial:
                                if picking.state in ['draft']:
                                    picking.action_confirm()
                                elif picking.state in ['confirmed']:
                                    picking.action_assign()
                                elif picking.state in ['assigned']:
                                    picking.button_validate()

                                wizard = self.env['stock.backorder.confirmation'].sudo().create(
                                    {'pick_ids': [(4, picking.id)]})
                                wizard.sudo().with_context(
                                    active_model='stock.picking',
                                    button_validate_picking_ids=[
                                        picking.id],
                                    default_show_transfers=False,
                                    default_pick_ids=[
                                        [4, picking.id]]
                                ).process()
                                backorder_id = self.env['stock.picking'].sudo().search(
                                    [('backorder_id', '=', picking.id)], limit=1)
                                if backorder_id:
                                    backorder.append(
                                        backorder_id.name)
                                if picking.state in ['done']:
                                    done_picking.append(picking.name)
                                else:
                                    not_done_picking.append(picking.name)
                            else:
                                if picking.state in ['draft']:
                                    picking.action_confirm()
                                if picking.state in ['confirmed']:
                                    picking.action_assign()
                                if picking.state in ['assigned']:
                                    picking.button_validate()
                                picking.button_validate()

                                if picking.state in ['done']:
                                    done_picking.append(picking.name)
                                else:
                                    not_done_picking.append(picking.name)
                        else:
                            is_partial = False
                            for move in picking.move_ids_without_package:
                                if move.state in ['confirmed', 'partially_available']:
                                    is_partial = True
                                move.sudo().write({
                                    'quantity': move.forecast_availability,
                                })
                            if is_partial:
                                if picking.state in ['draft']:
                                    picking.action_confirm()
                                if picking.state in ['confirmed']:
                                    picking.action_assign()
                                if picking.state in ['assigned']:
                                    picking.button_validate()

                                wizard = self.env['stock.backorder.confirmation'].sudo().create(
                                    {'pick_ids': [(4, picking.id)]})
                                wizard.sudo().with_context(
                                    active_model='stock.picking',
                                    button_validate_picking_ids=[
                                        picking.id],
                                    search_default_my_quotation=1,
                                    default_show_transfers=False,
                                    default_partner_id=picking.partner_id.id,
                                    default_picking_type_id=picking.picking_type_id.id,
                                    default_origin=picking.origin,
                                    default_group_id=picking.group_id.id,
                                    default_pick_ids=[
                                        [4, picking.id]],
                                    skip_immediate=True
                                ).process_cancel_backorder()
                                if picking.state in ['done']:
                                    done_picking.append(picking.name)
                                else:
                                    not_done_picking.append(picking.name)
                            else:
                                for move in picking.move_ids_without_package:
                                    move.sudo().write({
                                        'quantity': move.forecast_availability,
                                    })
                                if picking.state in ['draft']:
                                    picking.action_confirm()
                                if picking.state in ['confirmed']:
                                    picking.action_assign()
                                if picking.state in ['assigned']:
                                    picking.button_validate()
                                if picking.state in ['done']:
                                    done_picking.append(picking.name)
                                else:
                                    not_done_picking.append(picking.name)
            elif self.picking_validate_process == 'force':
                for picking in self.env['stock.picking'].search([('id', 'in', self.env.context.get('active_ids', False))]):

                    if picking.state in ['done']:
                        not_done_picking.append(picking.name)
                    else:
                        for move in picking.move_ids_without_package:
                            move.sudo().write({
                                'quantity': move.product_uom_qty,
                            })

                        if picking.state in ['draft']:
                            picking.action_confirm()
                        if picking.state in ['confirmed']:
                            picking.action_assign()
                        if picking.state in ['assigned']:
                            picking.with_context(force_validate=True).button_validate()
                        if picking.state in ['done']:
                            done_picking.append(picking.name)
                        else:
                            not_done_picking.append(picking.name)
            if len(done_picking) > 0:
                msg = "Following Picking Validated Successfully" + " " + ','.join(done_picking)
            if len(not_done_picking) > 0:
                message = "There is some issue to validate following Picking" + " " + ','.join(not_done_picking)
            if len(backorder)>0:
                backorder_message = "Backorders :" + " " + ','.join(backorder)
            return {
                'name': _('Picking Validate Success'),
                'type': 'ir.actions.act_window',
                'res_model': 'picking.warning.message',
                'view_type': 'form',
                'view_mode': 'form',
                'context': {'default_message': msg, 'default_compute_message': message,'default_backorder_message':backorder_message},
                'target': 'new'
            }
