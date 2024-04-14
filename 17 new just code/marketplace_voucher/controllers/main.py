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
from odoo import api, fields, models, _
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_voucher.controllers.main import website_voucher
from odoo.addons.marketplace_seller_wise_checkout.controllers.main import WebsiteSale as WebsiteSaleSellerWise

import logging
_logger = logging.getLogger(__name__)

class WebsiteSaleSellerWise(WebsiteSaleSellerWise):

    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        prod_obj = request.env['product.product'].browse(int(product_id))
        seller_id = prod_obj.sudo().marketplace_seller_id.id if prod_obj.sudo().marketplace_seller_id else False

        if line_id:
            order = request.env['sale.order.line'].sudo().browse(int(line_id)).order_id
        else:
            order = request.website.with_context(seller_id=seller_id).sale_get_order(force_create=True)
        self.wk_update_order_date(order)
        if order.state != 'draft':
            request.website.sale_reset(order_id= order.id if order.marketplace_seller_id else None)
            admin_qty = request.website.sale_get_order() and request.website.sale_get_order().cart_quantity or 0
            sellers_qty = 0
            seller_so_ids = request.session.get("seller_so_ids")
            if seller_so_ids:
                request.website._get_seller_sale_order_ids(seller_so_ids)
                seller_so_ids = request.env['sale.order'].sudo().browse(seller_so_ids)
                sellers_qty = sum(seller_so_ids.mapped('cart_quantity'))
            total_cart_qty = admin_qty + sellers_qty
            return {'total_cart_qty': total_cart_qty,'no_line':True,}

        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        if not order.cart_quantity:
            request.website.sale_reset(order_id= order.id if order.marketplace_seller_id else None)
            admin_qty = request.website.sale_get_order() and request.website.sale_get_order().cart_quantity or 0
            sellers_qty = 0
            seller_so_ids = request.session.get("seller_so_ids")
            if seller_so_ids:
                request.website._get_seller_sale_order_ids(seller_so_ids)
                seller_so_ids = request.env['sale.order'].sudo().browse(seller_so_ids)
                sellers_qty = sum(seller_so_ids.mapped('cart_quantity'))
            total_cart_qty = admin_qty + sellers_qty
            return {'total_cart_qty': total_cart_qty, 'no_line':True,}

        # order = request.website.sale_get_order(seller_id= seller_id)
        website_sale_order = request.website.get_admin_so_ids()
        value['notification_info'] = self._get_cart_notification_information(order, [value['line_id']])
        value['cart_ready'] = order._is_cart_ready()
        seller_so_ids = request.website.get_seller_so_ids()
        seller_so = seller_so_ids.filtered(lambda o: len(o.website_order_line)>0) if seller_so_ids else False
        admin_cart_qty = website_sale_order and website_sale_order.exists() and website_sale_order.cart_quantity or 0
        seller_cart_qty = seller_so and sum(seller_so.mapped('cart_quantity')) or 0
        value['cart_quantity'] = admin_cart_qty + seller_cart_qty
        from_currency = order.company_id.currency_id
        to_currency = order.pricelist_id.currency_id

        if not display:
            return value

        # count total cart quantity
        admin_qty = request.website.sale_get_order() and request.website.sale_get_order().cart_quantity or 0
        sellers_qty = 0
        seller_so_ids = request.session.get("seller_so_ids")
        if seller_so_ids:
            request.website._get_seller_sale_order_ids(seller_so_ids)
            seller_so_ids = request.env['sale.order'].sudo().browse(seller_so_ids)
            sellers_qty = sum(seller_so_ids.mapped('cart_quantity'))
        total_cart_qty = admin_qty + sellers_qty
        value['total_cart_qty'] = total_cart_qty
        # For validate the voucher coupon(START)
        request.website.validate_seller_wise_voucher_order(order)
        # For validate the voucher coupon(END)
        value['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'compute_currency': lambda price: from_currency._convert(
                price, to_currency, order.company_id, fields.Date.today()),
            'suggested_products': order._cart_accessories()
            })

        value['website_sale.total'] = request.env['ir.ui.view']._render_template("website_sale.total", {
            'website_sale_order': order,
            'compute_currency': lambda price: from_currency._convert(
                price, to_currency, request.env.user.company_id, fields.Date.today()),
        })
        return value



class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update_cart_voucher'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_cart_voucher(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        sol_obj = request.env['sale.order.line'].search([('id','=',line_id)])
        order = request.website.sale_get_order()
        secret_code = request.session.get('secret_key_data')
        if secret_code:
            voucher_product_id = request.env['ir.default'].sudo()._get('res.config.settings', 'wk_coupon_product_id')
            if set_qty == 0:
                product_obj = request.env['product.product'].search([('id','=',product_id)])
                if product_obj.marketplace_seller_id :
                    count = 0
                    for line in order.order_line:
                        if line.product_id.marketplace_seller_id:
                            if line.product_id.marketplace_seller_id == product_obj.marketplace_seller_id :
                                count = count+1
                    if count == 1:
                        for line in order.order_line:
                            if line.product_id.id == voucher_product_id:
                                secret_code = request.session.get('secret_key_data')
                                voucher_obj = request.env['voucher.voucher'].search([('id','=',secret_code.get('coupon_id'))])
                                if voucher_obj.marketplace_seller_id == product_obj.marketplace_seller_id:
                                    line.sudo().unlink()
                                    return voucher_product_id
        return True


class CustomWebsiteVoucher(website_voucher):

    @http.route()
    def voucher_call(self, secret_code=False, **post):
        seller_id = post.get('seller_id')
        try:
            result = {}
            voucher_obj = request.env['voucher.voucher']
            order= request.website.sale_get_order(seller_id=seller_id)
            wk_order_total = order.amount_total
            partner_id = request.env['res.users'].browse(request.uid).partner_id.id
            products =  []
            for line in order.order_line:
                products.append(line.product_id.id)
            result = voucher_obj.sudo().validate_voucher(secret_code, wk_order_total, products, refrence="ecommerce", partner_id=partner_id)
            if result['status']:
                final_result = request.website.sale_get_order(force_create=1, seller_id=seller_id)._add_voucher(wk_order_total, result)
                if not final_result['status']:
                    result.update(final_result)
                request.session['secret_key_data'] = {'coupon_id':result['coupon_id'],'total_available':result['total_available'],'wk_voucher_value':result['value'],'voucher_val_type':result['voucher_val_type'],'customer_type':result['customer_type']}
            return result
        except Exception as e:
            _logger.info('-------------Exception-----%r',e)
