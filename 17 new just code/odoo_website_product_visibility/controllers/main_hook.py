# # -*- coding: utf-8 -*-

# from odoo import http, tools, _
# from odoo.http import request
# from odoo.addons.http_routing.models.ir_http import slug
# from odoo.addons.website.controllers.main import QueryURL

# from odoo.addons.website_sale.controllers.main import TableCompute
# from odoo.addons.website_sale.controllers.main import WebsiteSale

# PPG = 20  # Products Per Page
# PPR = 4   # Products Per Row


# class WebsiteSale(WebsiteSale):

#     def _get_category_domain_hook(self):
#         return [('parent_id', '=', False)]

#     # def sitemap_shop(env, rule, qs): #odoo13
#     #     if not qs or qs.lower() in '/shop':
#     #         yield {'loc': '/shop'}

#     #     Category = env['product.public.category']
#     #     dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
#     #     dom += env['website'].get_current_website().website_domain()
#     #     for cat in Category.search(dom):
#     #         loc = '/shop/category/%s' % slug(cat)
#     #         if not qs or qs.lower() in loc:
#     #             yield {'loc': loc}

#     # @http.route([
#     #     '''/shop''',
#     #     '''/shop/page/<int:page>''',
#     #     '''/shop/category/<model("product.public.category"):category>''',
#     #     '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
#     # ], type='http', auth="public", website=True, sitemap=sitemap_shop) #odoo13
#     # def shop(self, page=0, category=None, search='', ppg=False, **post):
#     #     add_qty = int(post.get('add_qty', 1))
#     #     Category = request.env['product.public.category']
#     #     if category:
#     #         category = Category.search([('id', '=', int(category))], limit=1)
#     #         if not category or not category.can_access_from_current_website():
#     #             raise NotFound()
#     #     else:
#     #         category = Category

#     #     if ppg:
#     #         try:
#     #             ppg = int(ppg)
#     #             post['ppg'] = ppg
#     #         except ValueError:
#     #             ppg = False
#     #     if not ppg:
#     #         ppg = request.env['website'].get_current_website().shop_ppg or 20

#     #     ppr = request.env['website'].get_current_website().shop_ppr or 4

#     #     attrib_list = request.httprequest.args.getlist('attrib')
#     #     attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
#     #     attributes_ids = {v[0] for v in attrib_values}
#     #     attrib_set = {v[1] for v in attrib_values}

#     #     domain = self._get_search_domain(search, category, attrib_values)

#     #     keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

#     #     pricelist_context, pricelist = self._get_pricelist_context()

#     #     request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

#     #     url = "/shop"
#     #     if search:
#     #         post["search"] = search
#     #     if attrib_list:
#     #         post['attrib'] = attrib_list

#     #     Product = request.env['product.template'].with_context(bin_size=True)

#     #     search_product = Product.search(domain)
#     #     website_domain = request.website.website_domain()
#     #     categs_domain = [('parent_id', '=', False)] + website_domain
#     #     if search:
#     #         search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
#     #         categs_domain.append(('id', 'in', search_categories.ids))
#     #     else:
#     #         search_categories = Category
#     #     # categs = Category.search(categs_domain)
#     #     categs = Category.search(self._get_category_domain_hook()) #odoo13

#     #     if category:
#     #         url = "/shop/category/%s" % slug(category)

#     #     product_count = len(search_product)
#     #     pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
#     #     products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

#     #     ProductAttribute = request.env['product.attribute']
#     #     if products:
#     #         # get all products without limit
#     #         attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
#     #     else:
#     #         attributes = ProductAttribute.browse(attributes_ids)

#     #     layout_mode = request.session.get('website_sale_shop_layout_mode')
#     #     if not layout_mode:
#     #         if request.website.viewref('website_sale.products_list_view').active:
#     #             layout_mode = 'list'
#     #         else:
#     #             layout_mode = 'grid'

#     #     values = {
#     #         'search': search,
#     #         'category': category,
#     #         'attrib_values': attrib_values,
#     #         'attrib_set': attrib_set,
#     #         'pager': pager,
#     #         'pricelist': pricelist,
#     #         'add_qty': add_qty,
#     #         'products': products,
#     #         'search_count': product_count,  # common for all searchbox
#     #         'bins': TableCompute().process(products, ppg, ppr),
#     #         'ppg': ppg,
#     #         'ppr': ppr,
#     #         'categories': categs,
#     #         'attributes': attributes,
#     #         'keep': keep,
#     #         'search_categories_ids': search_categories.ids,
#     #         'layout_mode': layout_mode,
#     #     }
#     #     if category:
#     #         values['main_object'] = category
#     #     return request.render("website_sale.products", values)

#     # @http.route([
#     #     '/shop',
#     #     '/shop/page/<int:page>',
#     #     '/shop/category/<model("product.public.category"):category>',
#     #     '/shop/category/<model("product.public.category"):category>/page/<int:page>'
#     # ], type='http', auth="public", website=True)
#     # def shop(self, page=0, category=None, search='', ppg=False, **post):
#     #     if ppg:
#     #         try:
#     #             ppg = int(ppg)
#     #         except ValueError:
#     #             ppg = PPG
#     #         post["ppg"] = ppg
#     #     else:
#     #         ppg = PPG

#     #     if category:
#     #         category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
#     #         if not category:
#     #             raise NotFound()

#     #     attrib_list = request.httprequest.args.getlist('attrib')
#     #     attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
#     #     attributes_ids = {v[0] for v in attrib_values}
#     #     attrib_set = {v[1] for v in attrib_values}

#     #     domain = self._get_search_domain(search, category, attrib_values)

#     #     keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

#     #     compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()

#     #     request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

#     #     url = "/shop"
#     #     if search:
#     #         post["search"] = search
#     #     if attrib_list:
#     #         post['attrib'] = attrib_list

#     #     categs = request.env['product.public.category'].search(self._get_category_domain_hook())
#     #     Product = request.env['product.template']

#     #     parent_category_ids = []
#     #     if category:
#     #         url = "/shop/category/%s" % slug(category)
#     #         parent_category_ids = [category.id]
#     #         current_category = category
#     #         while current_category.parent_id:
#     #             parent_category_ids.append(current_category.parent_id.id)
#     #             current_category = current_category.parent_id

#     #     product_count = Product.search_count(domain)
#     #     pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
#     #     products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

#     #     ProductAttribute = request.env['product.attribute']
#     #     if products:
#     #         # get all products without limit
#     #         selected_products = Product.search(domain, limit=False)
#     #         attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
#     #     else:
#     #         attributes = ProductAttribute.browse(attributes_ids)

#     #     values = {
#     #         'search': search,
#     #         'category': category,
#     #         'attrib_values': attrib_values,
#     #         'attrib_set': attrib_set,
#     #         'pager': pager,
#     #         'pricelist': pricelist,
#     #         'products': products,
#     #         'search_count': product_count,  # common for all searchbox
#     #         'bins': TableCompute().process(products, ppg),
#     #         'rows': PPR,
#     #         'categories': categs,
#     #         'attributes': attributes,
#     #         'compute_currency': compute_currency,
#     #         'keep': keep,
#     #         'parent_category_ids': parent_category_ids,
#     #     }
#     #     if category:
#     #         values['main_object'] = category
#     #     return request.render("website_sale.products", values)

# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
