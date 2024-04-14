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
from odoo import models,api,fields,_
from odoo.exceptions import UserError
from datetime import date

import logging
_logger = logging.getLogger(__name__)


# flow for point value according to seller
point_value = 20

class WebsiteLoyaltyManagement(models.Model):
    _inherit = ['website.loyalty.management']

    mp_seller_id = fields.Many2one("res.partner",string="Seller",domain="[('seller','=',True)]",default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'])
    credit_base = fields.One2many(comodel_name="credit.base",inverse_name="loyalty_id",string="Credit Base")
    status = fields.Selection(selection=[('draft','Draft'),('pending','Pending'),('approved','Approved'),('reject','Reject')],string="Status",default="draft")
    website_published = fields.Boolean("Visible on Current website",default=False)
    website_id = fields.Many2one("website",string="Website")

    def website_publish_button(self):
        wk_seller_credit = self.env['website.loyalty.management'].search([('mp_seller_id.id','=',self.mp_seller_id.id),('status','=','approved'),('website_id.id','=',self.website_id.id),('website_published','=',True)])
        if wk_seller_credit and not self.id == wk_seller_credit.id:
            return {
                'name':'confirmation',
                'type':'ir.actions.act_window',
                'res_model': 'wk.publish.group',
                'view_mode':'form',
                'context': self._context,
                'target':'new',
            }
        else:
            self.website_published = False if self.website_published else True

    def set_to_pending(self):
        self.status = "pending"
    
    def set_to_approved(self):
        self.status = "approved"
    
    def set_to_rejected(self):
        self.website_published = False
        self.status = "reject"
    
    def set_to_draft(self):
        self.website_published = False
        self.status = "draft"

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            res = super().create(vals)
            if res.credit_base:
                amount_base = res.credit_base.filtered(lambda l:l.credit_base =='amount')
                price_base = res.credit_base.filtered(lambda l:l.credit_base =='product_price')
                if len(amount_base)>1 or len(price_base)>1:
                    raise UserError(_("Only one record for each Product price and Purchase amount ."))
            return res
    
    def write(self,vals):
        res = super().write(vals)
        for credit in self:
            if credit.credit_base:
                amount_base = credit.credit_base.filtered(lambda l:l.credit_base =='amount')
                price_base = credit.credit_base.filtered(lambda l:l.credit_base =='product_price')
                if len(amount_base)>1 or len(price_base)>1:
                    raise UserError(_("Only one record for each Product price and Purchase amount ."))
        return res

class WkLoyaltyRedeemHistory(models.Model):

    _inherit = "website.loyalty.history"

    mp_seller_id = fields.Many2one("res.partner",string="Seller",related="sale_order_ref.marketplace_seller_id")


    
