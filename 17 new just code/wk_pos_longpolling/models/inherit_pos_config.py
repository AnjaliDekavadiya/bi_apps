# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################

from odoo import api, fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_pos_longpolling = fields.Boolean(string="Enable Pos Real Time Update", default=True)