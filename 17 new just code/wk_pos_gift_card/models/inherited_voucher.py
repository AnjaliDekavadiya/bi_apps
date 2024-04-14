# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models, _
from odoo import tools
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class VoucherVoucher(models.Model):
    _inherit = "voucher.voucher"

    gift_card_voucher = fields.Boolean(
        string="Gfit Card Voucher")
    pos_order_line_id = fields.Many2one(
        comodel_name="pos.order.line",
        string="Order Line Id",
        help="This will be used for the domain purpose.")

    @api.model
    def get_pos_gift_card_voucher_values(self, line_id):
        product_id = line_id.product_id
        if product_id.wk_validity_unit == 'months':
            exp_date = str(datetime.today().date() +
                           relativedelta(months=product_id.wk_validity))
        else:
            exp_date = str(datetime.today().date() +
                           relativedelta(years=product_id.wk_validity))
        validity = (datetime.strptime(
            exp_date, '%Y-%m-%d').date() - datetime.today().date()).days
        vals = {
            'voucher_value': line_id.price_subtotal,
            'expiry_date': exp_date,
            'voucher_val_type': 'amount',
            'use_minumum_cart_value': False,
            'is_partially_redemed': product_id.wk_is_partially_redemed,
            # 'voucher_usage':'pos',
            'total_available': product_id.wk_redeemption_limit if product_id.wk_is_partially_redemed else 1,
            'issue_date': str(datetime.today().date()),
            'available_each_user': 1,
            'customer_type': 'general',
            'applied_on': 'all',
            'name': product_id.name,
            'validity': validity,
            'gift_card_voucher': True,
            'use_minumum_cart_value': product_id.wk_use_minimum_cart_value,
            'minimum_cart_amount': product_id.wk_minimum_cart_value,
        }
        return vals

    @api.model
    def create_pos_gift_card_voucher(self, line_id):
        vals = self.get_pos_gift_card_voucher_values(line_id)
        qty = line_id.qty
        while qty > 0:
            try:
                vals.pop('message_follower_ids', False)
                voucher_id = self.create(vals)
                vals.pop('voucher_code', False)
                vocuher_history_obj = self.env['voucher.history'].sudo().search(
                    [('voucher_id', '=', voucher_id.id), ('transaction_type', '=', 'credit')], limit=1)
                if vocuher_history_obj:
                    vocuher_history_obj.pos_order_id = line_id.order_id.id
                    vocuher_history_obj.pos_order_line_id = line_id.id
                    vocuher_history_obj.description = "Voucher Created at %s" % str(
                        datetime.today())
            except Exception as e:
                _logger.info(
                    '-------Exception in Creating Gift Card Voucher------%r', e)
                raise ValidationError(
                    ('Exception in Creating Gift Card Voucher %r' % e))
                pass
            qty -= 1
        return True
