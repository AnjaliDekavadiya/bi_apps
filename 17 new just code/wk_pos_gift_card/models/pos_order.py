# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import  ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, pos_order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(
            pos_order, draft, existing_order)
        tot = 0
        order = self.env['pos.order'].browse(order_id)
        for line in order.lines:
            price_subtotal = 0
            price_subtotal_incl = 0
            if line.product_id.wk_is_gift_card:
                qty = line.qty
                while line.qty > 1:
                    line_vals = {'product_id': line.product_id.id,
                                 'qty': 1,
                                 'price_unit': line.price_unit,
                                 'tax_ids': [(6, 0, line.tax_ids.ids)],
                                 'name': line.name,
                                 'discount': line.discount,
                                 'order_id': order.id,
                                 'price_subtotal': line.price_subtotal/qty,
                                 'price_subtotal_incl': line.price_subtotal_incl/qty,
                                 'create_date': str(datetime.today().date())
                                 }
                    new_line_id = self.env['pos.order.line'].create(line_vals)
                    values = new_line_id._compute_amount_line_all()
                    values['is_pos_gift_card'] = True
                    price_subtotal += values['price_subtotal']
                    price_subtotal_incl += values['price_subtotal_incl']
                    new_line_id.write(values)
                    self.env['voucher.voucher'].create_pos_gift_card_voucher(
                        new_line_id)
                    line.qty -= 1
                if qty > 1:
                    values = {}
                    values['price_subtotal'] = line.price_subtotal - \
                        price_subtotal
                    values['price_subtotal_incl'] = line.price_subtotal_incl - \
                        price_subtotal_incl
                    values['is_pos_gift_card'] = True
                    line.write(values)
                else:
                    line.is_pos_gift_card = True
                self.env['voucher.voucher'].create_pos_gift_card_voucher(line)
                tot += price_subtotal_incl + line.price_subtotal_incl
        return order.id

    @api.model
    def get_gift_vouchers(self, order_pos_reference):
        voucer_ids = []
        for pos_reference in order_pos_reference:
            order = self.search([('pos_reference', '=', pos_reference)])
            for line in order.lines:
                if line.product_id.wk_is_gift_card:
                    history_id = self.env['voucher.history'].search(
                        [('pos_order_line_id', '=', line.id), ('transaction_type', '=', 'credit')], limit=1)
                    voucer_ids.append(history_id.voucher_id.id)

        return voucer_ids


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    is_pos_gift_card = fields.Boolean(
        string="Is POS Gift Card Line", default=False)

    def print_pos_gift_card_voucher(self):
        if self.product_id.wk_is_gift_card:
            history_id = self.env['voucher.history'].search(
                [('pos_order_line_id', '=', self.id), ('transaction_type', '=', 'credit')], limit=1)
            if history_id:
                return self.env.ref('wk_coupons.coupons_report').report_action(history_id.voucher_id)
            else:
                raise ValidationError(
                    'There is not any voucher in this order line.')
        else:
            raise ValidationError(
                'There is not any voucher in this order line')
