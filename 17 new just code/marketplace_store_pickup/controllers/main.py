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
from odoo.addons.shipping_per_product.controllers.main import ProductShipping
from odoo.addons.website_sale.controllers.main import TableCompute, QueryURL
from odoo.addons.odoo_marketplace.controllers.main import MarketplaceSellerShop

import datetime
import logging
_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

SPG = 20  # Shops/sellers Per Page
SPR = 4   # Shops/sellers Per Row

TIME_TEMP = {
    'sunday': 0,
    'monday': 1,
    'tuesday': 2,
    'wednesday': 3,
    'thusday': 4,
    'friday': 5,
    'saturday': 6,
}

class MarketplaceSellerShop(MarketplaceSellerShop):

    @http.route(['/seller/shop/<int:shop_id>',
        '/seller/shop/<int:shop_id>/page/<int:page>',
        '/seller/shop/<shop_url_handler>',
        '/seller/shop/<shop_url_handler>/page/<int:page>'], type='http', auth="public", website=True)
    def seller_shop(self, shop_id=None, shop_url_handler=None, page=0, category=None, search='', ppg=False, **post):
        shop_obj = url = False
        uid, context, env = request.uid, dict(request.env.context), request.env
        if shop_url_handler:
            shop_obj = env["seller.shop"].sudo().search([("url_handler", "=", str(shop_url_handler))], limit=1)
            url = "/seller/shop/" + str(shop_obj.url_handler)
        elif shop_id:
            shop_obj = env["seller.shop"].sudo().browse(shop_id)
            wk_name = shop_obj.sudo().name.strip().replace(" ", "-")
            url = '/seller/shop/' + wk_name + '-' + str(shop_obj.id)
        if not shop_obj:
            return False

        def _get_search_domain(search):
            domain = request.website.sale_product_domain()
            domain += [("marketplace_seller_id", "=",
                        shop_obj.sudo().seller_id.id)]

            if search:
                for srch in search.split(" "):
                    domain += [
                        '|', '|', '|', ('name', 'ilike',
                                        srch), ('description', 'ilike', srch),
                        ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]
            product_obj = request.env['product.template'].sudo().search(domain)
            return request.env['product.template'].browse(product_obj.ids)

        uid, context, env = request.uid, dict(request.env.context), request.env
        url = "/seller/shop/" + str(shop_obj.url_handler)
        if search:
            post["search"] = search

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        if not context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = env['product.pricelist'].sudo().browse(context['pricelist'])

        sales_count = 0
        all_products = request.env['product.template'].sudo().search(
            [("marketplace_seller_id", "=", shop_obj.sudo().seller_id.id)])
        for prod in all_products:
            sales_count += prod.sales_count

        attrib_list = request.httprequest.args.getlist('attrib')
        url_for_keep = '/seller/shop/' + str(shop_obj.url_handler)
        keep = QueryURL(url_for_keep, category=category and int(
            category), search=search, attrib=attrib_list)

        product_count = request.env["product.template"].sudo().search_count([('sale_ok', '=', True), ('status', '=', "approved"), ("website_published", "=", True), ("id", "in", shop_obj.sudo().seller_product_ids.ids)])
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        total_product_ids = shop_obj.seller_product_ids.ids if shop_obj.seller_product_ids else []
        products = env['product.template'].sudo().search([('id', 'in', total_product_ids), ('sale_ok', '=', True), ('status', '=', "approved"), ("website_published", "=", True)], limit=ppg, offset=pager['offset'], order='website_published desc, website_sequence desc')

        from_currency = env['res.users'].sudo().browse(uid).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: env['res.currency'].sudo()._compute(from_currency, to_currency, price)
        shop_banner_url = request.website.image_url(shop_obj, 'shop_banner')

        values = {
            'shop_obj': shop_obj,
            'search': search,
            'rows': PPR,
            'bins': TableCompute().process(products if not search else _get_search_domain(search), ppg),
            'pager': pager,
            'products': products if not search else _get_search_domain(search),
            "keep": keep,
            'compute_currency': compute_currency,
            "pricelist": pricelist,
            'hide_pager': len(_get_search_domain(search)),
            'shop_banner_url': shop_banner_url,
            "sales_count": sales_count,
            "product_count": int(product_count)
        }

        return request.render("odoo_marketplace.mp_seller_shop", values)


    @http.route('/seller/shop/recently-product/', type='json', auth="public", website=True)
    def seller_shop_recently_product(self, shop_id, page=0, category=None, search='', ppg=False, **post):
        uid, context, env = request.uid, dict(request.env.context), request.env
        url = "/seller/shop/" + str(shop_id)
        shop_obj = env["seller.shop"].sudo().browse(shop_id)

        page = 0
        category = None
        search = ''
        ppg = False

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        if not context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = env['product.pricelist'].sudo().browse(context['pricelist'])

        attrib_list = request.httprequest.args.getlist('attrib')
        keep = QueryURL('/shop', category=category and int(category),
                        search=search, attrib=attrib_list)

        total_product_ids = shop_obj.seller_product_ids.ids if shop_obj.seller_product_ids else []
        recently_product_obj = request.env['product.template'].search([('id', 'in', total_product_ids), ('status', '=', "approved"), ("website_published", "=", True)], order='create_date desc, website_published desc, website_sequence desc', limit=env['ir.default']._get('res.config.settings', 'recently_product'))

        product_count = len(recently_product_obj.ids)
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=20, scope=7, url_args=post)
        product_ids = request.env['product.template'].search([("id", "in", recently_product_obj.ids)], limit=ppg, offset=pager[
                                                             'offset'], order='website_published desc, website_sequence desc')
        products = env['product.template'].browse(product_ids.ids)

        from_currency = env['res.users'].sudo().browse(uid).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: env['res.currency'].sudo()._compute(from_currency, to_currency, price)

        values = {
            'rows': PPR,
            'bins': TableCompute().process(products, ppg),
            'pager': pager,
            'products': products,
            "keep": keep,
            'compute_currency': compute_currency,
            "pricelist": pricelist,
            'shop_obj': shop_obj,
        }
        return request.env.ref('odoo_marketplace.shop_recently_product')._render(values, engine='ir.qweb')

class SellerStorePickup(http.Controller):

    @http.route(['/store/pickup/map'], type='json', auth="public", methods=['POST'], website=True)
    def store_pickup_map(self,**post):
        store_list = post.get('product_store_ids',False)
        product_store_ids = request.env["seller.shop"].sudo().browse(store_list)
        selected_id = post.get('selected_store_id',False)
        values = {
            'product_store_ids' : product_store_ids,
            'selected_id' : int(selected_id) if selected_id else False,
        }
        # return request.env.ref("marketplace_store_pickup.select_store_pickup_on_map")._render(values, engine='ir.qweb')
        return request.env['ir.qweb']._render('marketplace_store_pickup.select_store_pickup_on_map',values)

    @http.route(['/seller/store/update_sol_update'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def seller_store_update_sol_update(self, **post):
        so_details = post.get("so_details",False)
        if so_details:
            for data in so_details:
                order_lines = request.env["sale.order.line"].sudo().browse(data['line_ids'])
                store_id = int(data['store_id'])
                pickup_date = data['pickup_date']
                pickup_time = data['pickup_time']
                pickup_data2 = pickup_date.split("-")
                pickup_d = pickup_data2[1]+'/'+pickup_data2[2] +'/'+ pickup_data2[0]
                order_lines.set_store_pickup(store_id=store_id, pickup_date=pickup_d, pickup_time=pickup_time)
        return True

    def convert_float_in_time(self, time):
        return str(datetime.timedelta(hours=time))[:-3]

    def convert_to_slots(self, start, end):
        slots = []
        temp = start
        slot_count = int(end-start)
        for i in range(slot_count):
            slots.append((self.convert_float_in_time(temp), self.convert_float_in_time(temp+1)))
            temp = temp+1
        return slots

    @http.route(['/selected/store/details'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def selected_store_details(self, **post):
        shop_id = post.get('store_id', False)
        shop_obj = request.env["seller.shop"].sudo().browse(int(shop_id))
        order_line_id = post['order_lines']
        if order_line_id:
            order_line_id = order_line_id[0]
        data = {
            0: 'closed', 1: 'closed',2: 'closed',3: 'closed',
            4: 'closed',5: 'closed',6: 'closed',
        }
        for day in shop_obj.store_timing:
            if day.status == 'open':
                data[TIME_TEMP[day.days]] = self.convert_to_slots(day.open_time,day.close_time)
        values = {
            'product_store' : shop_obj,
            'line_id' : order_line_id
        }
        # return { 'data' : request.env.ref("marketplace_store_pickup.selected_store_pickup_view")._render(values), 'store_time' : data }
        return { 'data' : request.env['ir.ui.view']._render_template("marketplace_store_pickup.selected_store_pickup_view", values), 'store_time' : data }


class ProductShipping(ProductShipping):

    @http.route(['/shop/sol/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_shop_sol_carrier(self, **post):
        order_lines = post.get('order_lines')
        order_lines = request.env["sale.order.line"].sudo().browse(order_lines)
        order_lines = order_lines.filtered(lambda rec: rec.is_store_pickup)
        if order_lines:
            order_lines.remove_store_pickup()
        return super(ProductShipping, self).update_shop_sol_carrier(**post)
