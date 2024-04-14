# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, UserError
from odoo.tools import float_round
import logging
_logger = logging.getLogger(__name__)

class RmaMessageSuccessful(models.TransientModel):
    _name = 'rma.message.successful'
    _description = "Rma Message Successful"

    text = fields.Text("Message")


class RmaWizard(models.TransientModel):
    _name = 'rma.wizard'
    _description = 'RMA Wizard'

    @api.model
    def get_request_type(self):
        ir_default = self.env['ir.default'].sudo()
        is_repair_enable = ir_default._get('res.config.settings', 'is_repair_enable')
        irmodule_obj = self.env['ir.module.module']
        vals = irmodule_obj.sudo().search([('name', 'in', ['repair']), ('state', 'in', [
            'to install', 'installed', 'to upgrade'])])
        request_type = [('refund', 'Refund'), ('exchange', 'Exchange')]
        _logger.info(f"\n\n ======{self.env.context.get('delivered_ids')}======== \n\n")
        if vals and is_repair_enable:
            request_type.append(("repair", "Repair"))
        return request_type

    name = fields.Many2one('product.product', "Product", readonly=True)
    wk_order_id = fields.Many2one('sale.order', 'Order No', readonly=True)
    qty_return = fields.Float('Quantity Return')
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    problem = fields.Text('Problem', required=True)
    return_request_type = fields.Selection(
        'get_request_type', string="Return Request Type", default="refund")
    reason_id = fields.Many2one("rma.reasons", string="Reason")

    lot_serial_ids = fields.Many2many(
        string='Lot/Serial Number',
        comodel_name='stock.lot',
        required=True,
        domain=lambda self: [('id', 'in', self.env.context.get('delivered_ids'))]
    ) 

    tracking_type = fields.Char(
        string='Tracking Type',
    )    

    @api.model
    def create_method(self):
        sale_order_line_obj = self.env['sale.order.line'].browse(
            self.env.context['active_id'])
        sale_order_qty = sale_order_line_obj.qty_delivered
        rma_pool = self.env['rma.rma']
        rma_refund_qty = 0.0
        actual_rma_refund_qty = 0.0
        remaining_qty = 0.0
        rma_search_ids = rma_pool.search([('partner_id', '=', sale_order_line_obj.order_partner_id.id), (
            'product_id', '=', sale_order_line_obj.product_id.id), ('order_id', '=', sale_order_line_obj.order_id.id)])
        for rma_id in rma_search_ids:
            rma_obj = rma_pool.browse(rma_id.id)
            rma_refund_qty = rma_refund_qty + rma_obj.refund_qty
        actual_rma_refund_qty = rma_refund_qty + self.qty_return
        remaining_qty = sale_order_qty - rma_refund_qty

        rma_refund_qty = float_round(rma_refund_qty, precision_rounding=0.001)
        actual_rma_refund_qty = float_round(actual_rma_refund_qty, precision_rounding=0.001)
        remaining_qty = float_round(remaining_qty, precision_rounding=0.001)
        if self.qty_return <= 0:
            raise UserError(_("You cannot return the Product with quantity less than one !!!"))
        elif actual_rma_refund_qty > sale_order_qty:
            raise UserError(_("You cannot return the Product quantity greater than %s !!!") % (remaining_qty))
        elif self.name.tracking == 'serial' and self.qty_return != len(self.lot_serial_ids.ids):
            raise UserError(('Selected Quantities and the selected lot/serial number must be equal!!'))

        else:
            vals = {
                'order_id': self.wk_order_id.id,
                'refund_qty': self.qty_return,
                'product_id': self.name.id,
                'problem': self.problem,
                'partner_id': self.partner_id.id,
                'return_request_type': self.return_request_type,
                'reason_id' : self.reason_id.id,
                'orderline_id': sale_order_line_obj.id,
            }
            if self.name.tracking == 'serial':
                vals.update({
                    'lot_serial_ids': [(6,0,self.lot_serial_ids.ids)]
                })

            rma = rma_pool.sudo().create(vals)
            rma_local = rma_pool.search([('id', '=', rma.id)])
            rma_local.message_post(
                body=_("%s Generated Successfully" % rma.name), subtype_xmlid='mail.mt_comment')
            return rma

    def create_rma_button(self):
        self.ensure_one()
        rma = self.create_method()
        rma_no = rma.name
        text = 'Your RMA With No.%s Has Been Generated Successfully !!!' % rma_no
        partial_id = self.env['rma.message.successful'].create({'text': text})
        return {
            'name': "Message",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'rma.message.successful',
            'res_id': partial_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context
        }

    def create_and_view_rma_button(self):
        self.ensure_one()
        rma = self.create_method()
        if rma:
            return self.open_rma(rma.id)

    def open_rma(self, rma_id):
        ir_model_data = self.env['ir.model.data']
        form_res = self.env.ref('rma.rma_form_id').id
        form_id = form_res or False
        tree_res = self.env.ref('rma.rma_tree_id').id
        tree_id = tree_res or False
        return {
            'name': _('RMA CREATED'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'rma.rma',
            'res_id': rma_id,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': "",
            'type': 'ir.actions.act_window',
        }
