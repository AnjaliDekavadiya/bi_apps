# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug


class GlobalController(http.Controller):

    @http.route('/global/search', type='json', auth='public', website=True)
    def search_category(self,**kw):
        category_data = []
        Product_Category = request.env['product.public.category'].search([])
        for category in Product_Category:
            category_dis = {'id':category.id,'name':category.display_name}
            category_data.append(category_dis)
        return category_data

    @http.route(['/website_global_search_odoo/search'], type='http', auth="public", website=True,search='')
    def product_search(self,**post):
#        if post.get('category_id') != 'All Category':
        if post.get('category_id') != '':
            url = "/shop/category/%s?search=%s"%(post['category_id'],post['search'])
        else:
            url = "/shop?search=%s"%post['search']
        return request.redirect(url)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
