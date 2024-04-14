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
import odoo
from odoo import api, http, tools, _
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

import logging
_logger = logging.getLogger(__name__)

class PaypalExpressCheckout(http.Controller):

    @http.route(['/get/paypal/acquirer/details',], type='json', auth="public", methods=['POST'], website=True)
    def get_paypal_acquirer_details(self, **post):
        acquirer = request.env['payment.provider'].sudo().search([('code', '=', 'paypal_express'),('state','!=','disabled')], limit=1)
        if post.get("sale_order",False):
            order_id = request.env["sale.order"].sudo().browse(post.get("sale_order"))
        else:
            order_id = request.website.sale_get_order()
        data = {
            'acquirer_id':acquirer.id if acquirer else False,
            'enable_pro':acquirer.product_paypal if acquirer else False,
            'enable_cart':acquirer.cart_paypal if acquirer else False,
            'currency_id' : request.website.currency_id.id,
            'partner_id'   : order_id.partner_id.id,
            'flow'          : 'redirect',
            'tokenization_requested' : False,
            'landing_route': "/shop/payment/validate",
            'access_token': order_id.access_token,
            'sale_order' : order_id.id,
            'amount'    :  order_id.amount_total,
            'payment_method_id': acquirer.payment_method_ids[0].id,
        }
        return data

    @http.route(['/get/product/order/details',], type='json', auth="public", methods=['POST'], website=True)
    def get_product_order_details(self, **post):
        product_id = post.get('product_id')
        set_qty = post.get('add_qty')
        sale_order = request.website.sudo().sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sudo().sale_get_order(force_create=True)
        sale_order.order_line.sudo().unlink()
        sale_order._cart_update(
            product_id=int(product_id),
            set_qty=set_qty,
        )
        request.session['sale_last_order_id'] = sale_order.id
        if not sale_order.access_token:
            sale_order._portal_ensure_token()
        return {
            'sale_order': sale_order.id
        }
