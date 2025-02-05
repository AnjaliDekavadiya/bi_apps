# -*- coding: utf-8 -*-
#################################################################################
#    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from . import models
from . import wizards
from . import controllers
from odoo.exceptions import UserError

def pre_init_check(cr):
	from odoo.service import common
	version_info = common.exp_version()
	server_serie = version_info.get('server_serie')
	if not (16 < float(server_serie) <= 17):
		raise UserError(
			'Module support Odoo series 17.0 found {}.'.format(server_serie))
	return True
