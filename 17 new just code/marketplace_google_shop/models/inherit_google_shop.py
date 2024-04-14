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
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class GoogleShop(models.Model):
    _inherit = 'google.shop'

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', default=_set_seller_id)

    def _get_product_domain(self):
        f_domain = [("sale_ok", "=", True),("website_published","=",True)]
        if self.marketplace_seller_id:
            f_domain = [("sale_ok", "=", True),("website_published","=",True),('marketplace_seller_id','=',self.marketplace_seller_id.id),('status','=','approved')]
        return f_domain

    @api.onchange('marketplace_seller_id')
    def onchange_mp_seller(self):
        self.product_ids_rel = [(6,0,[])]
        self.oauth_id = None

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if self._context.get("mp_seller_google_shop"):
                seller_google_shop = self.search([('marketplace_seller_id','=',vals['marketplace_seller_id']),('content_language','=',vals['content_language'])])
                if seller_google_shop:
                    raise UserError('Only one shop can be created for a corresponding language.')

            res = super(GoogleShop,self).create(vals)
            return res


class ProductMapping(models.Model):
    _inherit = 'product.mapping'

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', default=_set_seller_id)
