# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo import SUPERUSER_ID,_
from odoo.http import request
from odoo.exceptions import UserError
from odoo import api, fields , models
from .website_loyalty_management import Policy

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	def _default_wk_loyalty_program_id(self):
		return self.env['website.loyalty.management'].get_active_obj().id

	wk_loyalty_program_id = fields.Many2one(
		string = 'Default Program',
		related='website_id.wk_loyalty_program_id',
		comodel_name = 'website.loyalty.management',
		domain = [('active','=',1)],
		readonly=False
	)

class website(models.Model):

	_inherit='website'

	def _default_wk_loyalty_program_id(self):
		return self.env['website.loyalty.management'].get_active_obj().id

	wk_loyalty_program_id = fields.Many2one(
		string = 'Default Program',
		comodel_name = 'website.loyalty.management',
		default = _default_wk_loyalty_program_id
	)

	@api.model
	def format_loyalty_points(self,loyalty_points):
		return loyalty_points

	@api.model
	def get_loaylity_policy(self,loyalty_id):
		return _(dict(Policy).get(loyalty_id.redeem_policy))

	@api.model
	def get_active_loyalty_obj(self,sale_order=None):
		order = sale_order or self.sale_get_order()
		loyalty_id= order.wk_loyalty_program_id if order else  self.wk_loyalty_program_id
		return loyalty_id

	@api.model
	def get_rewards(self,order_id):
		sale_order_amount = order_id.amount_total
		partner_id = order_id.partner_id
		loyalty_obj=self.get_active_loyalty_obj(sale_order=order_id)
		result=loyalty_obj._get_loyalty_amount(sale_order_amount,partner_id)
		partner_id.wk_website_loyalty_points = result['remain_points']
		res=loyalty_obj._get_loyalty_sale_line_info()
		self.env['website.virtual.product'].add_virtual_product(
			order_id=order_id.id,
			product_id=res['product_id'],
			product_name=res['name'],
			description=res['description'],
			product_price=-result['reward_amount'],
			redeem_points=result['redeem_point']    ,
			virtual_source='wk_website_loyalty'
		)
		loyalty_obj._save_redeem_history(order_id)
		return result
