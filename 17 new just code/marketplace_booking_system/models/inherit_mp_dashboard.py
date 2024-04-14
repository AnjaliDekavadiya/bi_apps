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

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class marketplace_dashboard(models.Model):
    _inherit = "marketplace.dashboard"

    def _get_approved_count(self):
        res = super(marketplace_dashboard, self)._get_approved_count()
        for rec in self:
            if rec.state == 'bookings':
                if rec.is_seller:
                    user_obj = self.env['res.users'].browse(self._uid)
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=',user_obj.partner_id.id), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'approved')])
                else:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'approved')])
                rec.count_product_approved = len(obj)
        return res

    def _get_pending_count(self):
        res = super(marketplace_dashboard, self)._get_pending_count()
        for rec in self:
            if rec.state == 'bookings':
                user_obj = self.env['res.users'].browse(rec._uid)
                if rec.is_seller:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=',user_obj.partner_id.id), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'pending')])
                else:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'pending')])
                rec.count_product_pending = len(obj)
        return res
    
    def _get_new_count(self):
        res = super(marketplace_dashboard, self)._get_new_count()
        for rec in self:
            if rec.state == 'bookings':
                user_obj = self.env['res.users'].browse(rec._uid)
                if rec.is_seller:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=',user_obj.partner_id.id), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'new')])
                else:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'new')])
                rec.count_product_new = len(obj)
        return res
    
    def _get_done_count(self):
        res = super(marketplace_dashboard, self)._get_done_count()
        # for rec in self:
        #     if rec.state == 'bookings':
        #         user_obj = self.env['res.users'].browse(rec._uid)
        #         if rec.is_seller:
        #             obj = self.env['sale.order.line'].search(
        #                 [('marketplace_seller_id', '=',user_obj.partner_id.id), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'new')])
        #         else:
        #             obj = self.env['sale.order.line'].search(
        #                 [('marketplace_seller_id', '!=', False), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'new')])
        #         rec.count_product_new = len(obj)
        for rec in self :
            if rec.is_seller:
                user_obj = self.env['res.users'].browse(rec._uid)
                obj = self.env['sale.order.line'].search(
                    [('marketplace_seller_id', '=',user_obj.partner_id.id), ('product_id.is_booking_type','=', True) ,('marketplace_state', '=', 'done'),('state', 'not in', ('draft', 'sent'))])
            else:
                obj = self.env['sale.order.line'].search(
                    [('marketplace_seller_id', '!=', False), ('product_id.is_booking_type','=', True) , ('marketplace_state', '=', 'done'),('state', 'not in', ('draft', 'sent'))])
            rec.count_product_done = len(obj)
        return res

    def _get_rejected_count(self):
        res = super(marketplace_dashboard, self)._get_rejected_count()
        for rec in self:
            if rec.state == 'bookings':
                user_obj = self.env['res.users'].browse(rec._uid)
                if rec.is_seller:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=',user_obj.partner_id.id), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'shipped')])
                else:
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('product_id.is_booking_type','=', True), ('marketplace_state', '=', 'shipped')])
                rec.count_product_rejected = len(obj)
        return res

    state = fields.Selection(selection_add=[('bookings', 'Bookings')])