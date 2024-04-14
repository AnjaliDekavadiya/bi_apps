# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api,models,tools
from logging import getLogger
_logger = getLogger(__name__)

class IrConfigParameter(models.Model):
	_inherit = 'ir.config_parameter'

	@api.model
	@tools.ormcache('self.env.cr.dbname')
	def _get_delay(self):
		"""
		@tools.ormcache is a decorator which helps to store dataset in memory cache. This is the methodology to manage cache for your functions.
		For example there is method which calls every time when you reload any page at Odoo then every time it execute definition of that function. Due to this page takes to much time to load.
		So in order to avid this issue Odoo introduces this decorator which stores the method response in memory cache. Then whenever someone trigger this method then instead of executing definition of this method it takes the response directly from cache.
		"""
		return int(
			self.env['ir.config_parameter'].sudo().get_param(
				'odoo_user_login_security.inactive_session_time_out_delay',0,
			)
		)

	@api.model
	@tools.ormcache('self.env.cr.dbname')
	def _get_urls(self):
		"""
		@tools.ormcache is a decorator which helps to store dataset in memory cache. This is the methodology to manage cache for your functions.
		For example there is method which calls every time when you reload any page at Odoo then every time it execute definition of that function. Due to this page takes to much time to load.
		So in order to avid this issue Odoo introduces this decorator which stores the method response in memory cache. Then whenever someone trigger this method then instead of executing definition of this method it takes the response directly from cache.
		"""
		return self.env['ir.config_parameter'].sudo().get_param(
			'odoo_user_login_security.inactive_session_time_out_ignored_url','',
		).split(',')

	def write(self, vals):

		"""
		Now in case you change setting then you can clear cache in write function using "clear_cache()",
		"""
		res = super(IrConfigParameter, self).write(vals)
		self._get_delay.cache.add_value(self, cache_value=int(self.env['ir.config_parameter'].sudo().get_param(
			'odoo_user_login_security.inactive_session_time_out_delay')))
		# self._get_delay.clear_cache(
		# 	self.filtered(
		# 		lambda r: r.key == 'odoo_user_login_security.inactive_session_time_out_delay'
		# 	),
		# )
		self._get_urls.cache.add_value(self, cache_value=self.env['ir.config_parameter'].sudo().get_param(
			'odoo_user_login_security.inactive_session_time_out_ignored_url'))
		# self._get_urls.clear_cache(
		# 	self.filtered(
		# 		lambda r: r.key == 'odoo_user_login_security.inactive_session_time_out_ignored_url'
		# 	),
		# )
		return res
