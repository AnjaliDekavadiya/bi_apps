# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	# time for a session logout in case of inactivity from user in session  
	inactive_session_time_out_delay = fields.Integer(
		string = 'Admin Session Lifetime (seconds)',
		config_parameter = 'odoo_user_login_security.inactive_session_time_out_delay',
	)
	# url which will be ingnored while timeout of session (inactivity from user in session)   
	inactive_session_time_out_ignored_url = fields.Char(
		string = 'Urls to be Ignored in User Activities',
		config_parameter = 'odoo_user_login_security.inactive_session_time_out_ignored_url',
		required = True,
	)
	# days after the session will be end 
	end_inactive_session_after = fields.Integer(
		string = 'End Sessions after Days without activity',
		config_parameter = 'odoo_user_login_security.end_inactive_session_after',
	)

	# days after the session will be cleared 
	clear_inactive_session_after = fields.Integer(
		string = 'Clear Inactive Sessions after Days',
		config_parameter = 'odoo_user_login_security.clear_inactive_session_after',
	)
	# forbid_multiple_sessions = fields.Boolean(
	# 	string = 'Forbid Simultaneous Sessions',
	# 	config_parameter = 'odoo_user_login_security.forbid_multiple_sessions',
	# )
	# override_past_session = fields.Boolean(
	# 	string = 'Force login',
	# 	config_parameter = 'odoo_user_login_security.override_past_session',
	# )

	# this allows user/admin to login with multile session 
	allow_multiple_session = fields.Selection(
		selection = [('yes', 'Multiple'), ('single', 'Single')],
		string = 'Admin Account Sharing',
		default = 'yes',
		required = True,
		config_parameter = 'odoo_user_login_security.allow_multiple_session',
	)

	# this allows user to terminate the past sessions/ restrict user to login
	# admin user session cannot be restricted to login but can be terminated
	override_past_session = fields.Selection(
		selection = [('yes', 'Yes'), ('no', 'No')],
		string = 'Force login',
		default = 'yes',
		required = True,
		config_parameter = 'odoo_user_login_security.override_past_session',
	)

	#numbers of login failures after which account will be locked out 
	login_cooldown_after = fields.Integer(
		string = 'Maximum Login Failures to Lockout Account',
		config_parameter = 'base.login_cooldown_after',
	)

	#seconds user will able to loing again 
	login_cooldown_duration = fields.Integer(
		string = 'Lockout Time (Seconds)',
		config_parameter = 'base.login_cooldown_duration',
	)
	password_reset_attempt_limit = fields.Integer(
		string = 'Max Number of Password Reset Requests',
		config_parameter = 'odoo_user_login_security.password_reset_attempt_limit',
	)
	password_reset_attempt_expiration = fields.Integer(
		string = 'Recovery Link Expiration Period (hours)',
		config_parameter = 'odoo_user_login_security.password_reset_attempt_expiration',
	)
	password_reset_attempt_gap = fields.Integer(
		string = 'Min Time Between Password Reset Requests',
		config_parameter = 'odoo_user_login_security.password_reset_attempt_gap',
	)
	password_lifetime = fields.Integer(
		string = 'Password Lifetime (days)',
		config_parameter = 'odoo_user_login_security.password_lifetime',
	)
	forced_password_change = fields.Boolean(
		string = 'Redirect to Change Password',
		config_parameter = 'odoo_user_login_security.forced_password_change',
	)
	send_failed_login_email = fields.Boolean(
		string = 'Send Email on Failed Login',
		config_parameter = 'odoo_user_login_security.send_failed_login_email',
	)
	send_suspicious_login_email = fields.Boolean(
		string = 'Send Email on Suspicious Login',
		config_parameter = 'odoo_user_login_security.send_suspicious_login_email',
	)

	# minimum inactive session time out delay calculation(it will reset to 60 if seconds are less than 60)
	@api.onchange('inactive_session_time_out_delay')
	def _onchange_inactive_session_time_out_delay(self):
		if self.inactive_session_time_out_delay <= 0:
			self.inactive_session_time_out_delay = 0
		elif self.inactive_session_time_out_delay < 60:
			self.inactive_session_time_out_delay = 60
		elif self.inactive_session_time_out_delay > 31536000:
			self.inactive_session_time_out_delay = 31536000

	# setting  clear clear inactive session after 90 by default 
	@api.onchange('clear_inactive_session_after')
	def _onchange_clear_inactive_session_after(self):
		if self.clear_inactive_session_after <= 0:
			self.clear_inactive_session_after = 90

	# setting  clear inactive session after 7 by default 
	@api.onchange('end_inactive_session_after')
	def _onchange_end_inactive_session_after(self):
		if self.end_inactive_session_after <= 0:
			self.end_inactive_session_after = 7

	# setting  login cooldown after  5 attemts by default 
	@api.onchange('login_cooldown_after')
	def _onchange_login_cooldown_after(self):
		if self.login_cooldown_after <= 0:
			self.login_cooldown_after = 5

	# setting  login cooldown after  60 seconds by default 
	@api.onchange('login_cooldown_duration')
	def _onchange_login_cooldown_duration(self):
		if self.login_cooldown_duration <= 0:
			self.login_cooldown_duration = 60

	# managing negative values 
	@api.onchange('password_reset_attempt_limit')
	def _onchange_password_reset_attempt_limit(self):
		if self.password_reset_attempt_limit < 0:
			self.password_reset_attempt_limit = 0

	# managing negative values 
	@api.onchange('password_reset_attempt_expiration')
	def _onchange_password_reset_attempt_expiration(self):
		if self.password_reset_attempt_expiration < 0:
			self.password_reset_attempt_expiration = 0

	# managing negative values 
	@api.onchange('password_lifetime')
	def _onchange_password_lifetime(self):
		if self.password_lifetime < 0:
			self.password_lifetime = 0
