# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>;)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
##########################################################################
from odoo import models, api, fields


class PosOrder(models.Model):

    _inherit = 'pos.order'

    # -------------------------------------------------------------------------//
    # MODEL FIELDS
    # -------------------------------------------------------------------------//
    booking_id = fields.Many2one('hotel.booking', string="Hotel Booking")
    # state = fields.Selection(
    #     selection_add=[('unpaid_invoice', 'Unpaid Invoice')])

    # -------------------------------------------------------------------------
    # Override
    # -------------------------------------------------------------------------
    @api.model
    def _order_fields(self, ui_order):
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        fields_return.update({
            'booking_id': ui_order.get('booking_id', False),
        })
        return fields_return

    @api.model
    def _process_order(self, order, draft, existing_order):
        res = super(PosOrder, self)._process_order(order, draft, existing_order)
        pos_order = self.browse(res)
        if pos_order.booking_id and pos_order.to_invoice:
            pos_order._generate_pos_order_invoice()
        return res

    # -------------------------------------------------------------------------
    # LOW-LEVEL METHODS
    # -------------------------------------------------------------------------
    def write(self, vals):
        for order in self:
            # if vals.get('state') and vals['state'] == 'invoiced' and order.name == '/' and order.booking_id:
            if order.name == '/' and order.booking_id:
                vals['name'] = self._compute_order_name()
        return super(PosOrder, self).write(vals)

    def action_pos_order_paid(self):
        if not self.booking_id:
            return super(PosOrder, self).action_pos_order_paid()