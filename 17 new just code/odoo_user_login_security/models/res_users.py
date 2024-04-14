# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from logging import getLogger

from odoo import _,fields,models,SUPERUSER_ID
from odoo.http import request


_logger = getLogger(__name__)


class ResUsers(models.Model):
	_inherit = 'res.users'

	session_ids = fields.One2many(
		comodel_name='session.session',
		inverse_name='user_id',
		string='Sessions',
	)

	def write(self,vals):
		if 'password' in vals:
			vals['last_password_reset'] = fields.datetime.utcnow()
			for rec in self:
				rec.terminate_sessions()
		return super().write(vals)


	def terminate_sessions(self):
		self.env['session.session'].search([('user_id','in',self.ids)]).terminate()

	def recommend_password_update(self):
		self.ensure_one()
		self.env['mail.message'].create(
			 {
				'message_type': 'notification',
				'subtype_id': self.env.ref('mail.mt_comment').id,
				'author_id': self.sudo().browse(SUPERUSER_ID).partner_id.id,
				'subject': 'Password too old',
				'body': 'It is recommended to update password.',
				'partner_ids': [(4, self.partner_id.id)],
			}
		)

	def _totp_check(self, code):
		res = super()._totp_check(code)
		user = self.sudo()
		totp = user.totp_enabled
		if totp:
			session = self.env['session.session'].save_session(user.id)
			if session:
				request.session['usersession'] = session.id
		return res
