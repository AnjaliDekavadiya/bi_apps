# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import http
from odoo.tools.translate import _
from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.website.controllers.main import Website
from werkzeug.exceptions import NotFound

import logging
_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):

	@http.route()
	def shop_payment(self, **post):
		res = super(WebsiteSale, self).shop_payment(**post)
		return res

	@http.route()
	def product(self, product, category='', search='', **kwargs):
		res = super(WebsiteSale, self).product(product, category, search, **kwargs)
		if not product.check_website_accessibility():
			raise NotFound()
		return res

	@http.route()
	def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
		res = super(WebsiteSale, self).shop(page=page, category=category, search=search, min_price=min_price, max_price=max_price, ppg=ppg, post=post)
		if category:
			category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
			if not category or (category.website_ids and request.website.id not in category.website_ids.ids):
				raise NotFound()
		categ = res.qcontext.get('categories')
		search_categories_ids = res.qcontext.get('search_categories_ids')
		if categ:
			categ = categ.filtered(lambda c: request.website.id in c.website_ids.ids or not c.website_ids)
			res.qcontext.update({'categories': categ})
		if search_categories_ids:
			search_categories_ids = request.env['product.public.category'].browse(search_categories_ids)
			search_categories_ids = search_categories_ids.filtered(lambda c: request.website.id in c.website_ids.ids or not c.website_ids)
			res.qcontext.update({'search_categories_ids': search_categories_ids})
		return res
