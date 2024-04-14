# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  'name'         : 'Odoo User Login Security',
  'summary'      : '''Secure your Odoo from Intruders with User Login Security''',
  'category'     : 'Extra Tools',
  'version'      : '1.0.4',
  'sequence'     : 1,
  'author'       : 'Webkul Software Pvt. Ltd.',
  'license'      : 'Other proprietary',
  'website'      : 'https://store.webkul.com/Odoo-User-Login-Security.html',
  'description'  : '''''',
  'live_test_url': 'https://odoodemo.webkul.com/?module=odoo_user_login_security',
  'depends'      : ['auth_signup'],
  'data'         : [
		'security/security.xml',
		'security/ir.model.access.csv',
		'views/dashboard.xml',
		'views/res_users.xml',
		'views/session.xml',
		'views/res_config_settings.xml',
		'templates/mail.xml',
		'data/ir_actions_server.xml',
		'data/ir_cron.xml',
		'data/ir_config_parameter.xml',
	],
	'demo': [
		'demo/security.xml',
		'demo/session.session.csv',
	],
  'assets': {
	'web.assets_frontend': [
	  '/odoo_user_login_security/static/src/js/login.js',
	],
	'web.assets_backend':    [
		'/odoo_user_login_security/static/src/css/dashboard.css',
	  '/odoo_user_login_security/static/src/css/owl.carousel.min.css',
	  '/odoo_user_login_security/static/src/css/owl.theme.default.min.css',
	  '/odoo_user_login_security/static/src/js/jquery.mousewheel.min.js',
	  '/odoo_user_login_security/static/src/js/owl.carousel.min.js',
		'/odoo_user_login_security/static/src/js/dashboard.js',
		'/odoo_user_login_security/static/src/xml/dashboard.xml',
	]
  },
  'images'       : ['static/description/banner.png'],
  'application'  : True,
  'price'        : 99,
  'currency'     : 'USD',
  'pre_init_hook': 'pre_init_check',
}
