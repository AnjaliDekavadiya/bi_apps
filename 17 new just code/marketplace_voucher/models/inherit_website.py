# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from odoo import api, fields, models, _
from odoo import tools
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
	_inherit = 'website'

	@api.model
	def get_voucher_product_price(self, sale_order, voucher_obj, voucher_product_id):
		res = super(Website, self).get_voucher_product_price(sale_order, voucher_obj, voucher_product_id)
		if voucher_obj and voucher_obj.marketplace_seller_id:
			order_lines = sale_order.order_line.filtered(lambda l: l.product_id.marketplace_seller_id and
				l.product_id.marketplace_seller_id.id == voucher_obj.marketplace_seller_id.id and not l.is_delivery)
			if order_lines:
				order_total_price = sum(order_lines.mapped("price_subtotal"))
				res.update({'order_total_price':order_total_price})
		return res
		
	def validate_seller_wise_voucher_order(self, sale_order):
		order_total_price = 0
		voucher_obj = self.get_current_order_voucher(sale_order)
		if voucher_obj and hasattr(sale_order,'order_line'):
			voucher_product_id = self.wk_get_default_product()
			if isinstance(voucher_product_id, (list)):
				voucher_product_id = voucher_product_id[0]
			res = self.get_voucher_product_price(sale_order, voucher_obj, voucher_product_id)
			selected_prod_percent_price = res['selected_prod_percent_price']
			order_total_price = res['order_total_price']
			self.set_voucher_sale_order_price(sale_order, voucher_obj, voucher_product_id, selected_prod_percent_price, voucher_obj.id, order_total_price)
