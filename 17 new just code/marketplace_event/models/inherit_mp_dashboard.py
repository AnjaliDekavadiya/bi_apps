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

    state = fields.Selection(selection_add=[('events', 'Events')])

    def _get_approved_count(self):
        super(marketplace_dashboard, self)._get_approved_count()
        for rec in self:
            if rec.state == 'events':
                if rec.is_user_seller():
                    user_id = self.env['res.users'].search([('id', '=', rec._uid)])
                    seller_id = user_id.partner_id.id
                    obj = self.env['event.event'].search([('marketplace_seller_id', '=', seller_id), ('status', '=', 'approved')])
                else:
                    obj = self.env['event.event'].search([('marketplace_seller_id', '!=', False), ('status', '=', 'approved')])
                rec.count_product_approved = len(obj)

    def _get_pending_count(self):
        super(marketplace_dashboard, self)._get_pending_count()
        for rec in self:
            if rec.state == 'events':
                if rec.is_user_seller():
                    user_id = self.env['res.users'].search([('id', '=', rec._uid)])
                    seller_id = user_id.partner_id.id
                    obj = self.env['event.event'].search([('marketplace_seller_id', '=', seller_id), ('status', '=', 'pending')])
                else:
                    obj = self.env['event.event'].search([('marketplace_seller_id', '!=', False), ('status', '=', 'pending')])
                rec.count_product_pending = len(obj)

    def _get_rejected_count(self):
        super(marketplace_dashboard, self)._get_rejected_count()
        for rec in self:
            if rec.state == 'events':
                if rec.is_user_seller():
                    user_id = self.env['res.users'].search([('id', '=', rec._uid)])
                    seller_id = user_id.partner_id.id
                    obj = self.env['event.event'].search(
                        [('marketplace_seller_id', '=', seller_id), ('status', '=', 'rejected')])
                else:
                    obj = self.env['event.event'].search(
                        [('marketplace_seller_id', '!=', False), ('status', '=', 'rejected')])
                rec.count_product_rejected = len(obj)
    
