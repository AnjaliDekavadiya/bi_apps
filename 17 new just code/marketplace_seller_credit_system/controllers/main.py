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
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_loyalty_management.controllers.controller import website_loaylty_management
import logging
_logger = logging.getLogger(__name__)

class Website_Loyalty_Management(website_loaylty_management):


    def validate_redeem(self,post,values,loyalty_obj,partner_id,sale_order):
        if sale_order.marketplace_seller_id:
            redeem_rule_id =  sale_order._get_seller_redeem_rule_id(loyalty_obj,sale_order.customer_loyalty_points)
            if not redeem_rule_id:
                values['no_redeem_rule_match'] =True

            elif not redeem_rule_id.reward:
                values['no_reward_rule'] =True
            else:
                res=self._allowed_redeem(partner_id ,loyalty_obj ,redeem_rule_id,sale_order,values)
                if res:
                    values.update(res)
            return values
        else:
            return super().validate_redeem(post,values,loyalty_obj,partner_id,sale_order)

    def _allowed_redeem(self,partner_id ,loyalty_obj ,redeem_rule_id,sale_order,values):
        if sale_order.marketplace_seller_id:
            reward = redeem_rule_id.reward
            sale_order_amount = sale_order.amount_total

            computed_amount = partner_id.wk_website_loyalty_points if not sale_order.marketplace_seller_id else sale_order.customer_loyalty_points
            max_redeem_amount = loyalty_obj.max_redeem_amount

            eligible_amount = computed_amount < max_redeem_amount and computed_amount  or     max_redeem_amount
            reduced_amount = sale_order_amount  < eligible_amount and sale_order_amount  or      eligible_amount
            diff=sale_order_amount < eligible_amount and sale_order_amount or   eligible_amount
            values['reduced_amount'] = reduced_amount
            values['reduced_point'] = reward and reduced_amount/reward
            values['allowed_redeem'] = 'partial_redeem'
            if loyalty_obj.redeem_policy == 'one_time_redeem':
                values['allowed_redeem'] = 'one_time_redeem'
                percent_benefit = round((diff*100/eligible_amount),2)
                values['percent_benefit'] =percent_benefit
            return values
        else:
            return super()._allowed_redeem(partner_id,loyalty_obj,redeem_rule_id,sale_order,values)

    @http.route(['/loyality/get_reward/'] ,type = 'http' ,auth = "public" ,website = True )
    def get_reward(self ,**post ):
        sale_order = request.website.sale_get_order()
        if sale_order.marketplace_seller_id:
            result=sale_order.get_seller_rewards()
            if result.get('reward_amount'):
                request.session['reward']='Taken'
                request.session['reward']=result.get('reward_amount')
        else:
            res = super().get_reward(**post)
        return request.redirect("/shop/payment")




 