# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from re import match
from logging import getLogger
from urllib import response

from odoo import exceptions,http
from odoo.http import root,request, FilesystemSessionStore 
from odoo.tools import config,func
from odoo.tools._vendor import sessions


_logger = getLogger(__name__)


class Session(http.Session):
	def authenticate(self, dbname, login=None, password=None):
		"""
		Authenticate the current user with the given dbname, login and
		password. If successful, store the authentication parameters in the
		current session and request.
        """
		_logger.info("****************************authenticate is working****************************")
		try:
			return super(Session,self).authenticate(dbname, login, password)
		except exceptions.AccessDenied:
			if request.registry.get('session.session'):
				uid = request.env.user.search([('login','=',login)]).id
				session = request.env['session.session'].save_session(uid=uid,state='error')
				if session:
					session.send_login_email(status='error')
			raise
	

class Application(http.Application):
	@func.lazy_property
	def session_store(self):
		_logger.info("****************************session store is working****************************%r",config.session_dir)
		"""Setup http sessions"""
		path = config.session_dir
		_logger.debug('HTTP sessions stored in: %s', path)
		# return sessions.FilesystemSessionStore(path,session_class=Session)
		return FilesystemSessionStore(path,session_class=Session)
		
class Request(http.Request):

	def _get_session_and_dbname(self):
		_logger.info("****************************get session and dbname is working****************************")
		session, dbname = super(Request,self)._get_session_and_dbname()
		_logger.info("****************************get >>>>>>>>>>>>>>>>>working*********************************")
		session_id = self.httprequest.cookies.get('session_id')
		db = self.httprequest.cookies.get('db')
		is_db_path = match('\/web\?.*db=\w+',self.httprequest.full_path)
		if session_id and db and not session.db and not is_db_path:
			session.db = db
		return session, dbname





root.session_store = Application().session_store
root._get_session_and_dbname = Request(request.httprequest)._get_session_and_dbname


