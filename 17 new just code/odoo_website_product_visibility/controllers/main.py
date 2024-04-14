# -*- coding: utf-8 -*-

from odoo import http, tools, _
from odoo.http import request

# from odoo.addons.odoo_website_product_visibility.controllers.main_hook import WebsiteSale
from odoo.addons.website_sale.controllers.main import WebsiteSale

PPG = 20  # Products Per Page
PPR = 3   # Products Per Row


class WebsiteSale(WebsiteSale):


    # def _get_search_domain(self, search, category, attrib_values):
    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):  #odoo13
        res = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values,search_in_description)
        shop_visibility = request.env['public.shop.visibility']
        visibility = shop_visibility.sudo().search([])
        public_user = request.env.user.has_group('base.group_public')
        if not public_user:
            if request.env.user.partner_id.custom_prob_template_ids:
                res += [('id', 'in', request.env.user.partner_id.custom_prob_template_ids.ids)]
            if request.env.user.partner_id.custom_visibility_category_ids:
                res += [('public_categ_ids', 'in', request.env.user.partner_id.custom_visibility_category_ids.ids)]
        else:
            if not visibility.all_product:
                res += [('id', 'in', visibility.template_ids.ids)]
            if not visibility.all_category:
                res += [('public_categ_ids', 'in', visibility.category_ids.ids)]
        return res

    # def _get_category_domain_hook(self):
    #     cdomain = super(WebsiteSale, self)._get_category_domain_hook()
    #     shop_visibility = request.env['public.shop.visibility']
    #     visibility = shop_visibility.sudo().search([])
    #     public_user = request.env.user.has_group('base.group_public')
    #     if not public_user:
    #         if request.env.user.partner_id.category_ids:
    #             cdomain += [('id', 'in', request.env.user.partner_id.category_ids.ids)]
    #     else:
    #         if not visibility.all_category:
    #             cdomain += [('id', 'in', visibility.category_ids.ids)]
    #     return cdomain

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
