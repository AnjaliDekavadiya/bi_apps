# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo.tools.translate import _
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'

    def custome_action_cancel(self, cr, uid, ids, context=None):
        for pick in self.browse(cr, uid, ids, context=context):
            ids2 = [move.id for move in pick.move_ids]
            self.pool.get('stock.move').action_cancel(cr, uid, ids2, context)
            objs = self.pool.get('stock.move').browse(cr, uid, ids2)
            for i in objs:
                i.unlink()

        return True

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.po_id:
            self.po_id.invoice_status = 'to invoice'

        return res

    @api.model
    def _default_stage(self):
        st_ids = self.env['stage.master'].search([('draft', '=', True)])
        if st_ids:
            for st_id in st_ids:
                return st_id.id

    def change_state(self, context={}):
        if context.get('copy') == True:
            self.flag = True
        else:
            flag = 0
            flag1 = 0

            for picking_line in self.move_ids:
                if picking_line.quantity_done == 0:
                    flag = 1
                    break
                elif picking_line.product_uom_qty < picking_line.quantity_done:
                    flag1 = 1
                    break
                else:
                    flag = 0
                    flag1 = 0

            if flag:
                raise UserError(_("You haven't set processed quantities."))
            if flag1:
                raise UserError(_("product quantity exceed from related purchase order."))
            else:
                view_id = self.env.ref('pragtech_purchase.approval_wizard_form_view_purchase').id
                return {
                    'type': 'ir.actions.act_window',
                    'key2': 'client_action_multi',
                    'res_model': 'approval.wizard',
                    'multi': 'True',
                    'target': 'new',
                    'views': [[view_id, 'form']],
                }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['challan_no'] = self.env['ir.sequence'].get('stock.picking')
            existing_stage = []
            st_id = self.env['stage.master'].search([('draft', '=', True)])
            if self._context:
                msg_ids = {
                    'date': datetime.now(),
                    'from_stage': None,
                    'to_stage': st_id.id,
                    'remark': 'Created by ' + (self.env['res.users'].browse(self._context.get('uid'))).name,
                    'model': 'stock.picking'
                }
                existing_stage.append((0, 0, msg_ids))
                vals.update({'mesge_ids': existing_stage})

            return super(StockPicking, self).create(vals_list)

    project_wbs = fields.Many2one('project.task', 'Sub project', domain=[('is_wbs', '=', True), ('is_task', '=', False)], readonly=True)
    project_id = fields.Many2one('project.project', 'Project', readonly=True,domain=[('approval_state','=','approve')])

    sub_project = fields.Many2one('sub.project', 'Sub Project')

    type = fields.Selection([('from_supplier', 'Receipt from Supplier'), ('from_other_site', 'Receipt from Other site')], 'Type', readonly=True)
    invoice_no = fields.Char('Invoice No')
    invoice_date = fields.Datetime('Invoice Date')
    challan_no = fields.Char('Delivery Challan No')
    bill_id = fields.Char('Bill')
    stage_id = fields.Many2one('stage.master', 'Stage', default=_default_stage, readonly=True, copy=False)
    brand_id = fields.Many2one('brand.brand', 'Brand')
    vehicle_no = fields.Char('Vehicle No')
    transport_bill_id = fields.Char('Transport Bill')
    transport_amount = fields.Float('Transport Amount')
    loading_charges = fields.Float('Loading Charges')
    other_charges = fields.Float('Other Charges')
    other_charges2 = fields.Float('Other Charges2')
    gate_registration_no = fields.Char('Gate Registration No')
    gate_registration_date = fields.Datetime('Gate Registration Date')
    challan_date = fields.Datetime('Challan Date', default=datetime.now())
    challan_qty = fields.Integer('Challan Qty')
    flag = fields.Boolean('Flag', default=False)
    po_id = fields.Many2one('purchase.order', string='PO', readonly=True)
    mesge_ids = fields.One2many('mail.messages', 'res_id', string='Massage', domain=lambda self: [('model', '=', self._name)], auto_join=True, readonly=True)

    def _create_backorder(self, backorder_moves=[]):
        """ Move all non-done lines into a new backorder picking. If the key 'do_only_split' is given in the context, then move all lines not in context.get('split', []) instead of all non-done lines.
        """
        # TDE note: o2o conversion, todo multi
        backorders = self.env['stock.picking']
        for picking in self:
            backorder_moves = backorder_moves or picking.move_ids
            if self._context.get('do_only_split'):
                not_done_bo_moves = backorder_moves.filtered(lambda move: move.id not in self._context.get('split', []))
            else:
                not_done_bo_moves = backorder_moves.filtered(lambda move: move.state not in ('done', 'cancel'))

            if not not_done_bo_moves:
                continue

            backorder_picking = picking.copy({
                'name': '/',
                'move_ids': [],
                'pack_operation_ids': [],
                'backorder_id': picking.id
            })

            picking.message_post(body=_("Back order <em>%s</em> <b>created</b>.") % (backorder_picking.name))
            not_done_bo_moves.write({'picking_id': backorder_picking.id})
            if not picking.date_done:
                picking.write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

            backorder_picking.action_confirm()
            backorder_picking.action_assign()
            stage_obj = self.env['stage.master'].search([('draft', '=', True)])[0]
            pick_obj = backorders.browse(backorder_picking.id)
            pick_obj.flag = False
            pick_obj.stage_id = stage_obj
            backorders |= backorder_picking

        return backorders

    def action_cancel(self):
        po_obj = self.env['purchase.order']
        stage_obj = self.env['stage.master']
        po_req = self.env['purchase.requisition']
        mail_message = self.env['mail.messages']

        for picking in self:
            po_ids = po_obj.search([('id', '=', picking.po_id.id)])
            st_id = stage_obj.search([('approved', '=', True)])
            st_id_draft = stage_obj.search([('draft', '=', True)])

            for picking_line in picking.pack_operation_product_ids:
                po_req_ids = self.env['po.requisition'].search([('order_id', '=', po_ids.id), ('material_id', '=', picking_line.product_id.id)])

                purchase_line = self.env['purchase.order.line'].search([('order_id', '=', po_ids.id), ('product_id', '=', picking_line.product_id.id)])

                requisition = po_req.search([('name', '=', po_req_ids.requisition_id.name), ('material_id', '=', po_req_ids.material_id.id)])[0]

                vals = {
                    'project_id': requisition.project_id.id,
                    'project_wbs': requisition.project_wbs.id,
                    'rate': purchase_line.price_unit,
                    'unit': picking_line.product_uom_id.id,
                    'current_req_qty': picking_line.product_qty,
                    'material_id': picking_line.product_id.id,
                    'stage_id': st_id[0].id,
                    'specification': 'Release from' + ' ' + po_ids.name
                }
                requisition_id = po_req.create(vals)

                msg_ids = {
                    'date': datetime.now(),
                    'from_stage': st_id_draft[0].id,
                    'to_stage': st_id[0].id,
                    'remark': None,
                    'model': 'purchase.requisition',
                    'res_id': requisition_id
                }

                mail_message.create(msg_ids)
                backorder_pick_ids = self.search([('id', '=', picking.backorder_id.id)])
                stage_id = stage_obj.search([('foreclosed', '=', True)])
                backorder_pick_ids.write({'stage_id': stage_id[0].id})

        return super(StockPicking, self).action_cancel()


class StockMove(models.Model):
    _inherit = 'stock.move'
    _description = 'Stock Move'


class StockLocation(models.Model):
    _inherit = 'stock.location'
    _description = 'Stock Location'

    project_id = fields.Many2one('project.project', 'Project')

