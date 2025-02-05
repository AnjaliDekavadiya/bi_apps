# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from . import models
from odoo import api, SUPERUSER_ID

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import UserError
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if not 16.0 < float(server_serie) <= 17.0:
        raise UserError(f'Module support Odoo series 17.0 but found {server_serie}.')
    return True

def approve_all_timeslots_nd_plans(env):
    # env = api.Environment(cr, SUPERUSER_ID, {})
    booking_plans = env['booking.plan'].search([('marketplace_seller_id','=',False)])
    timeslots = env['booking.time.slot'].search([('marketplace_seller_id','=',False)])
    if booking_plans:
        booking_plans.write({'state':'approved'})
    if timeslots:
        timeslots.write({'state':'approved'})
