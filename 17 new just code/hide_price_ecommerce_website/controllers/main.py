# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. 
# See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    def _get_products_recently_viewed(self):
        results = super(WebsiteSale, self)._get_products_recently_viewed()
        if results:
            for res in results.get('products'):
                res['is_hide_price_on_shop_custom'] = not request.env.user.has_group('hide_price_ecommerce_website.group_website_shop_show_price') and request.website.is_hide_price_on_shop_custom
        return results

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
