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
from odoo import models,api,fields 
from odoo.http import request
from datetime import date

import logging
_logger = logging.getLogger(__name__)
  


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_loyalty_points = fields.Float("loyalty Points",compute="get_customer_points_for_seller")

    # approval domain and published domain applied here 
    def set_seller_loyalty_id(self):
        seller_loyalty = self.env['website.loyalty.management'].search([('mp_seller_id','=',self.marketplace_seller_id.id),('status','=','approved'),('website_published','=',True)])
        self.wk_loyalty_program_id = seller_loyalty if self.marketplace_seller_id else self.wk_loyalty_program_id



    def get_order_loyalty_points(self,loyalty_id):
        loyalty_base = loyalty_id.credit_base
        purchase_base = loyalty_base.filtered(lambda l:l.credit_base == 'amount')
        if purchase_base and self.amount_total>loyalty_id.min_purchase:
            offer_ratio = purchase_base.points / purchase_base.on_purchase
            return self.amount_total * offer_ratio
        else:
            product_base = loyalty_base.filtered(lambda l:l.credit_base == 'product_price')
            specific_base = loyalty_base.filtered(lambda l:l.credit_base == 'product_specific')
            specfic_product_ids = {l.product_id.id:(loyalty_id.min_purchase,l.points/l.on_purchase) for l in specific_base}
            wk_points = 0
            for line in self.order_line:
                get_specfic_base = specfic_product_ids.get(line.product_id.product_tmpl_id.id,False)
                if get_specfic_base  and line.price_subtotal>get_specfic_base[0]:
                    wk_points += get_specfic_base[1]*line.price_subtotal
                elif product_base and line.price_subtotal>loyalty_id.min_purchase:
                    offer_ratio = purchase_base.points / purchase_base.on_purchase if purchase_base.on_purchase else 1
                    wk_points += line.price_subtotal*offer_ratio
            return wk_points

    @api.depends('order_line.price_total')
    def _compute_wk_website_loyalty_points(self):
        for order in self:
            if order.marketplace_seller_id and order.wk_loyalty_state not in ['cancel', 'done']:
                amount = order.amount_total
                loyalty_id = order.wk_loyalty_program_id 
                loyalty_points = order.get_order_loyalty_points(loyalty_id)
                wk_website_loyalty_points = order.wk_extra_loyalty_points + loyalty_points
                order.update({
                    'wk_website_loyalty_points': round(wk_website_loyalty_points,2),
                })
            else:
                super(SaleOrder,self)._compute_wk_website_loyalty_points()

    @api.onchange("marketplace_seller_id")
    def get_customer_points_for_seller(self):
        for order in self:
            seller = order.marketplace_seller_id
            if seller:
                customer_history = self.env['website.loyalty.history'].search([('partner_id','=',order.partner_id.id),('mp_seller_id','=',seller.id)])
                additon_amount = sum(customer_history.filtered(lambda l : l.loyalty_process == 'addition').mapped('points_processed'))
                deduction_amount = sum(customer_history.filtered(lambda l : l.loyalty_process == 'deduction').mapped('points_processed'))
                applied_points = sum(self.order_line.filtered(lambda l:l.is_virtual).mapped('redeem_points'))
                customer_loyalty_points = additon_amount - deduction_amount - applied_points
                order.customer_loyalty_points = customer_loyalty_points if customer_loyalty_points>=0 else 0.0

            else:
                order.customer_loyalty_points = 0.0

    def _get_seller_loyalty_amount(self,loyalty_obj):
        result={'reward_amount': 0, 'remain_points': 0,'redeem_point': None}
        wk_website_loyalty_points = self.customer_loyalty_points
        sale_order_amount = self.amount_total
        if sale_order_amount > 1:
            max_redeem_amount=loyalty_obj.max_redeem_amount
            redeem_rule = loyalty_obj.redeem_rule_list
            redeem_rule_list=redeem_rule.filtered(
            lambda rule:rule.point_start<=wk_website_loyalty_points and
            rule.point_end>=wk_website_loyalty_points)
            if len(redeem_rule_list):
                redeem_rule_list = redeem_rule_list[0]


            computed_redeem_amount=wk_website_loyalty_points*redeem_rule_list.reward
            reduction_amount = computed_redeem_amount if computed_redeem_amount<max_redeem_amount else max_redeem_amount

            if loyalty_obj.redeem_policy == 'one_time_redeem':
                if sale_order_amount <= reduction_amount:
                    result['reward_amount'] = sale_order_amount
                else:
                    result['reward_amount'] = reduction_amount
                result['remain_points']=0
                result['redeem_point'] = wk_website_loyalty_points
            elif loyalty_obj.redeem_policy == 'partial_redeem' and redeem_rule_list.reward :
                if sale_order_amount <=    reduction_amount:
                    result['reward_amount'] = sale_order_amount
                    result['remain_points'] = abs((computed_redeem_amount-sale_order_amount)/redeem_rule_list.reward)
                    result['redeem_point'] = sale_order_amount/redeem_rule_list.reward
                else:
                    result['reward_amount'] = reduction_amount
                    result['remain_points'] = abs((computed_redeem_amount-reduction_amount)/redeem_rule_list.reward)
                    result['redeem_point'] = reduction_amount/redeem_rule_list.reward
        return result

    def get_seller_rewards(self):
        sale_order_amount = self.amount_total
        partner_id = self.partner_id
        loyalty_obj=self.wk_loyalty_program_id
        result=self._get_seller_loyalty_amount(loyalty_obj)
        res=loyalty_obj._get_loyalty_sale_line_info()
        self.env['website.virtual.product'].add_virtual_product(
			order_id=self.id,
			product_id=res['product_id'],
			product_name=res['name'],
			description=res['description'],
			product_price=-result['reward_amount'],
			redeem_points=result['redeem_point']    ,
			virtual_source='wk_website_loyalty'
		)
        loyalty_obj._save_redeem_history(self)
        return result

    def _get_seller_redeem_rule_id(self,loyalty_obj,wk_website_loyalty_points):
        return loyalty_obj.redeem_rule_list.filtered(
            lambda rule: rule.point_start <= wk_website_loyalty_points
            and rule.point_end >= wk_website_loyalty_points)
    
    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super()._create_invoices(grouped, final, date)
        for order in self:
            virtual_lines = order.order_line.filtered(lambda l : l.is_virtual)
            for v_lines in virtual_lines:
                if v_lines.invoice_lines:
                    v_lines.invoice_lines.write({'is_loyalty_line':True})
        return res




class Website(models.Model):

    _inherit = "website"

    def sale_get_order(self,*args,**kwargs):
        res = super().sale_get_order(*args, **kwargs)
        if res and res[0].marketplace_seller_id:  
            res.set_seller_loyalty_id()
        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_loyalty_line = fields.Boolean("Loyalty Benefit",default=False)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create_seller_payment_new(self, sellers_dict):
        seller_ids = sellers_dict.get('seller_ids')
        virtual_lines = self.invoice_line_ids.filtered(lambda l:l.is_loyalty_line)
        for i in seller_ids:
            seller_dict = seller_ids.get(i)
            if seller_dict and virtual_lines:
                commission = self.env['ir.default']._get('res.config.settings', 'mp_loyalty_commission')
                wk_commission_amount = virtual_lines.mapped('price_subtotal')
                if commission:
                    wk_commission_amount = [0]        
                    for v_lines in virtual_lines:
                        loyalty_amount = self.calculate_commission(v_lines.price_total, i)    
                        v_lines.seller_commission = abs(v_lines.price_total - loyalty_amount)  
                        v_lines.update_seller_admin_amount(loyalty_amount)
                        wk_commission_amount += [v_lines.price_total - v_lines.seller_commission]   
                sellers_dict['seller_ids'][i]['invoice_line_payment'] += wk_commission_amount 
                sellers_dict['seller_ids'][i]['invoice_line_ids'] += virtual_lines.mapped('id') 
        return super().create_seller_payment_new(sellers_dict)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mp_loyalty_commission = fields.Boolean("Commission on loyalty",default=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set('res.config.settings', 'mp_loyalty_commission', self.mp_loyalty_commission)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        mp_loyalty_commission = self.env['ir.default']._get('res.config.settings', 'mp_loyalty_commission')
        res.update(mp_loyalty_commission = mp_loyalty_commission)
        return res

class WkSellerCreditBase(models.Model):
    _name = "credit.base"

    name = fields.Char("Name")
    credit_base = fields.Selection(selection=[('amount','Puchase Amount'),('product_specific','Product Specific'),('product_price','Product Price')],string="Based On",default="amount",required=True)
    loyalty_id = fields.Many2one(comodel_name="website.loyalty.management",ondelete="cascade")
    points = fields.Float("Points",default=1)
    on_purchase = fields.Float("On Purchase",default=1)
    product_id = fields.Many2one(comodel_name="product.template",string="Product Id")

class InheritProductproduct(models.Model):
    _inherit = "product.product"

    is_credit = fields.Boolean("Credit Product",default=False)






