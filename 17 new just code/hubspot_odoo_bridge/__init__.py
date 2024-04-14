# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from . import models
from . import wizard
from . import controllers

def pre_init_check(cr):
	from odoo.service import common
	from odoo.exceptions import UserError
	version_info = common.exp_version()
	server_serie = version_info.get('server_serie')
	if not 16 < float(server_serie) <= 17:
		raise Warning(
            'Module support Odoo series 17.0 found {}.'.format(server_serie))

	try:
		import hubspot
	except ImportError:
		raise Warning(
			'Python package requirement unfulfilled. '
			'`python3 -m pip install hubspot-api-client==3.8.2`'
		)

	return True
