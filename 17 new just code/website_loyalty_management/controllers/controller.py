# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import route,request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal as WebsiteAccount, pager as portal_pager
import logging
_logger = logging.getLogger(__name__)

class website_loaylty_management(http.Controller):

    def validate_redeem(self,post,values,loyalty_obj,partner_id,sale_order):
        redeem_rule_id=loyalty_obj._get_redeem_rule_id(partner_id)
        if not redeem_rule_id:
            values['no_redeem_rule_match'] =True

        elif not redeem_rule_id.reward:
            values['no_reward_rule'] =True
        else:
            res=self._allowed_redeem(partner_id ,loyalty_obj ,redeem_rule_id,sale_order,values)
            if res:
                values.update(res)
        return values


    @http.route(['/loyalty/confirmation/'] ,type = 'json' ,auth = "public" ,website = True )
    def get_confimation(self , **post ):
        values = dict()
        partner_id= request.env.user.partner_id
        website = request.website
        sale_order =  website.sale_get_order()
        loyalty_obj = website.get_active_loyalty_obj(sale_order=sale_order)

        if request.env.user.id != request.env.ref('base.public_user').id:
            values['login'] = True
        if request.session.get('reward') == 'Taken':
            values['redeem_once'] =  True
        elif not sale_order or not len(sale_order) or sale_order.amount_total<0:
            values['no_order'] = True
        elif  partner_id.wk_website_loyalty_points<1:
            values['no_point'] = True
        elif len(loyalty_obj) == 0:
            values['no_loyality_feature'] = True
        elif  sale_order.amount_total<loyalty_obj.min_purchase  :
            values['min_purchase'] = True
        elif not loyalty_obj.redeem_rule_list:
            values['no_redeem_rule'] = True
        else:
            res = self.validate_redeem(post,values,loyalty_obj,partner_id,sale_order)
            values.update(res)
        response = request.env['ir.ui.view']._render_template("website_loyalty_management.message_template", values)
        return {'response':response}

    def _allowed_redeem(self ,partner_id ,loyalty_obj ,redeem_rule_id ,sale_order,values ):
        reward = redeem_rule_id.reward
        sale_order_amount = sale_order.amount_total

        computed_amount = partner_id.wk_website_loyalty_points*reward
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

    @http.route(['/loyality/get_reward/'] ,type = 'http' ,auth = "public" ,website = True )
    def get_reward(self ,**post ):
        result=request.website.get_rewards(request.website.sale_get_order())
        if result.get('reward_amount'):
            request.session['reward']='Taken'
            request.session['reward']=result.get('reward_amount')
        return request.redirect("/shop/cart/")



class WebsiteAccount(WebsiteAccount):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'points_count' in counters:
            points_count = request.env.user.wk_website_loyalty_points
            values['points_count'] = points_count
        return values

    @http.route(['/my/loyalty', '/my/loyalty/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_loyalty(self, page=1, **kw):
        HistorySudo = request.env['website.loyalty.history'].sudo()
        user = request.env.user
        domain = [('partner_id', '=', user.partner_id.id)]
        loyalty_count = HistorySudo.search_count(domain)
        pager = portal_pager(
            url="/my/loyalty",
            total=loyalty_count,
            page=page,
            step=self._items_per_page
        )
        histories = HistorySudo.search(domain, limit=self._items_per_page, offset=pager['offset'])
        values = {
                'histories': histories.sudo(),
                'page_name': 'loyalty',
                'pager': pager,
                'default_url': '/my/loyalty',
                'wk_website_loyalty_points': user.wk_website_loyalty_points
            }
        return  request.render("website_loyalty_management.my_loyalty", values)

class WebsiteSale(WebsiteSale):
    @http.route()
    def shop_payment(self, **post):
        order = request.website.sale_get_order(force_create=True)
        for order_line_id in order.order_line:
            if order_line_id.is_virtual:
                order_line_id.price_unit = order_line_id.reward_amount
        res = super(WebsiteSale,self).shop_payment(**post)
        return res

    @http.route('/shop/payment/get_status/<int:sale_order_id>' ,type='json' ,auth="public", website=True )
    def shop_payment_get_status(self ,sale_order_id ,**post):
        response=super(WebsiteSale,self).shop_payment_get_status(sale_order_id ,**post)
        order=request.env['sale.order'].sudo().browse(sale_order_id)

        loyalty_obj =request.website.get_active_loyalty_obj(sale_order=order)
        if len(loyalty_obj):
            res=loyalty_obj.update_partner_loyalty(order,'draft')
            loyalty_obj._save_redeem_history(order)
        request.session['reward']=''
        return response


    def remove_loyalty_txn_id(self):
        order = request.website.sale_get_order()
        if order:
            virtual_line=order.order_line.filtered(lambda line:line.is_virtual and (line.virtual_source=='wk_website_loyalty'))
            virtual_line.unlink()
            request.session['reward'] = ''
            request.env['website.loyalty.management'].sudo().cancel_redeem_history(order)
        return True


    @http.route()
    def pricelist_change(self, pricelist, **post):
        self.remove_loyalty_txn_id()
        res = super(WebsiteSale,self).pricelist_change(pricelist=pricelist,**post)
        return res


    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0,product_custom_attribute_values=None, no_variant_attribute_values=None,express=False, **kwargs):
        self.remove_loyalty_txn_id()
        res = super(WebsiteSale,self).cart_update(product_id=product_id, add_qty=add_qty, set_qty=set_qty,product_custom_attribute_values=product_custom_attribute_values, no_variant_attribute_values=no_variant_attribute_values,express=express, **kwargs)
        return res

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
                        product_custom_attribute_values=None, no_variant_attribute_values=None, **kw):
        self.remove_loyalty_txn_id()
        res = super(WebsiteSale, self).cart_update_json(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, display=display,
            product_custom_attribute_values=product_custom_attribute_values,no_variant_attribute_values=no_variant_attribute_values,**kw)
        sale_order = request.website.sale_get_order()
        if sale_order:
            loyalty_points = sale_order.wk_website_loyalty_points
            res.update({"Order_loyalty_points": str(round(loyalty_points,2))})
        return res

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def shop_payment_confirmation(self, **post):
        response=super(WebsiteSale,self).shop_payment_confirmation(**post)
        order = response.qcontext.get('order')
        if order:
            response.qcontext['wk_website_loyalty_points']=order.wk_website_loyalty_points
        return response

    @http.route(['/remove/virtualproduct/<temp>'] ,type='http' ,auth="public" ,website=True )
    def virtual_product_remove(self, temp):
        virtual_line=request.env['sale.order.line'].sudo().search(
            [('id', '=', temp),('virtual_source','=','wk_website_loyalty')]
        )
        if virtual_line:
            order = virtual_line.order_id
            virtual_line.unlink()
            request.session['reward'] = ''
        return request.redirect("/shop/cart")
