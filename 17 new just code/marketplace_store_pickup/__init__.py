# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2016-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# License URL :<https://store.webkul.com/license.html/>
##########################################################################
from . import controllers
from . import models
import logging
_logger = logging.getLogger(__name__)
from odoo import api, SUPERUSER_ID

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import UserError
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='17.0':raise UserError('Module support Odoo series 17.0 found {}.'.format(server_serie))
    return True

def assign_shop_group_to_seller(env):
    # env = api.Environment(cr, SUPERUSER_ID, {})
    seller_group_id = env['ir.model.data']._xmlid_lookup("%s.%s" % ('odoo_marketplace', 'group_marketplace_seller_shop'))[1]
    implied_group_id = env['ir.model.data']._xmlid_lookup("%s.%s" % ('odoo_marketplace', 'marketplace_seller_group'))[1]
    groups_obj = env["res.groups"].browse(seller_group_id)
    implied_groups = env["res.groups"].browse(implied_group_id)
    implied_groups.sudo().write({'implied_ids':[(4,seller_group_id)]})
