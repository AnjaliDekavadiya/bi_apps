# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
import traceback
from logging import getLogger
from os import utime
from os.path import getmtime
from time import time
import werkzeug
from odoo import models, SUPERUSER_ID
from odoo.http import request, root, SessionExpiredException,is_cors_preflight

_logger = getLogger(__name__)

class IrHttp(models.AbstractModel):
	_inherit = 'ir.http'



	@classmethod
	def _authenticate(cls, endpoint):
		"""
		check authentication level, if authentication completed check timeout.
		"""
		try:
			res = super()._authenticate(endpoint=endpoint)
			cls._timeout_check()
			return res
		except SessionExpiredException:
			request.env['session.session']._logout('unknown')
			# _logger.error(traceback.format_exc()) #Uncomment it to diagnose
			raise

	@classmethod
	def _timeout_check(cls):
		if request.httprequest.path in request.env['ir.config_parameter']._get_urls():
			return

		if not request.uid or request.uid == SUPERUSER_ID:
			return

		# Calculate deadline
		delay = request.env['ir.config_parameter']._get_delay()
		deadline = time() - delay if delay > 0 else False

		# Check if past deadline
		expired = False
		path = root.session_store.get_session_filename(request.session.sid)
		if deadline:
			try:
				expired = getmtime(path) < deadline
			except OSError:
				_logger.debug('Exception reading session file modified time.')

		# If timeout, terminate
		if expired and request.session.db and request.session.uid:
			# request.session.logout(keep_db=True)
			# request.env['session.session']._logout('timed_out')
			pass

		# Else, update session last modified/access times
		else:
			try:
				utime(path, None)
			except OSError:
				_logger.debug('Exception updating session file access/modified times.')

	@classmethod
	def _post_dispatch(cls, response):
		super()._post_dispatch(response)
		if request.registry and request.uid:
			if request.db and request.registry.get('session.session')  and  request.params.get('login_success'):
				known_users = request.httprequest.cookies.get('known_users', '') or ''
				known_users_list = [u_id for u_id in known_users.split(',') if u_id] 
				session = request.env['session.session'].sudo().save_session()
				if str(request.uid) not in known_users_list and session:
					session.send_login_email(status='suspicious')
					known_users_list.append(str(request.uid))
					response.set_cookie('known_users', ",".join(known_users_list))
		
	

