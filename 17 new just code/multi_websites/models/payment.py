# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
class PaymentTransaction(models.Model):
	_inherit = 'payment.transaction'

	website_id = fields.Many2one('website',
		string='Website',
		readonly=True
	)

	@api.model
	def create(self, vals):
		res = super(PaymentTransaction, self).create(vals)
		if res.reference:
			order_string = res.reference.split('-')
			order_id = self.env['sale.order'].search([('name','=',order_string[0])], limit=1)
			if order_id and order_id.website_id:
				res.website_id = order_id.website_id.id
		return res
