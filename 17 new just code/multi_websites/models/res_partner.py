# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request
from odoo import api, fields, models
class ResPartner(models.Model):
	_inherit = 'res.partner'

	website_ids = fields.Many2many(
		comodel_name='website',
		string="Websites"
	)

class ResUsers(models.Model):
	_inherit = 'res.users'

	@api.model
	def _signup_create_user(self, values):
		new_user = super(ResUsers, self)._signup_create_user(values)
		current_website = self.env['website'].get_current_website()
		if request and current_website.specific_user_account and new_user.partner_id:
			new_user.partner_id.website_id = current_website
		return new_user

	@api.model
	def _get_login_domain(self, login):
		res =  super(ResUsers, self)._get_login_domain(login)
		website = self.env['website'].get_current_website()
		if website.users_login_multi_websites:
			user = request.env['res.users'].browse(request._uid)
			user.sudo().partner_id.website_ids = [(4,website.id)]
			return [res[0]]
		return res
