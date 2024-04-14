# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import models
from itertools import groupby
from odoo.osv.expression import AND
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def get_formatted_channel_name(self, db_name, config_id, channel='wk_pos_longpolling'):
        return '{}_{}_{}'.format(db_name, channel, config_id)
    
    def get_pos_ui_product_product_by_params(self, custom_search_params):
        try:
            notifications = []
            channel = self.get_formatted_channel_name(self.env.cr.dbname, self.config_id.id)
            notifications.append([channel, "websocket_status", []])
            self.env['bus.bus']._sendmany(notifications)
        except Exception as e:
            _logger.info("############ webscoket first notification failed for real time ###########")
        return super().get_pos_ui_product_product_by_params(custom_search_params)
    