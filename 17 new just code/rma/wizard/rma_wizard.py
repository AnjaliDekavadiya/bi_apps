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
from odoo.exceptions import RedirectWarning,UserError
import logging
_logger = logging.getLogger(__name__)

class rma_message_successful(models.TransientModel):
    _name = 'rma.message.successful'
    _description = "Rma Message Successful"

    text = fields.Text("Message")

rma_message_successful()


class rma_wizard(models.TransientModel):
    _name = 'rma.wizard'
    _description = "Rma Wizard"

    name = fields.Many2one('product.product', "Product", readonly=True)
    wk_order_id = fields.Many2one('sale.order', 'Order No', readonly=True)
    qty_return = fields.Float('Quantity Return')
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    problem = fields.Text('Problem', required=True)

    @api.model
    def create_method(self):
        sale_order_line_obj = self.env['sale.order.line'].browse(
            self.env.context['active_id'])
        sale_order_qty = sale_order_line_obj.qty_delivered
        rma_pool = self.env['rma.rma']
        rma_refund_qty = 0
        actual_rma_refund_qty = 0
        remaining_qty = 0
        rma_search_ids = rma_pool.search([('partner_id', '=', sale_order_line_obj.order_partner_id.id), (
            'product_id', '=', sale_order_line_obj.product_id.id), ('order_id', '=', sale_order_line_obj.order_id.id)])
        for rma_id in rma_search_ids:
            rma_obj = rma_pool.browse(rma_id.id)
            rma_refund_qty = rma_refund_qty + rma_obj.refund_qty
        actual_rma_refund_qty = rma_refund_qty + self.qty_return
        remaining_qty = sale_order_qty - rma_refund_qty
        if self.qty_return <= 0:
            raise UserError(_("You cannot return the Product with quantity less than one !!!"))
        elif actual_rma_refund_qty > sale_order_qty:
            raise UserError(_("You cannot return the Product quantity greater than %s !!!") % (remaining_qty))
        else:
            rma = rma_pool.sudo().create({
                'order_id': self.wk_order_id.id,
                'refund_qty': self.qty_return,
                'product_id': self.name.id,
                'problem': self.problem,
                'partner_id': self.partner_id.id,
                'orderline_id': sale_order_line_obj.id,
            })
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

rma_wizard()
