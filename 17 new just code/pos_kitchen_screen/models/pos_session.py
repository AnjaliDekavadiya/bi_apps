# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import  models, _
import datetime
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_kitchen_screen_config(self):
        return {'search_params': {'domain': [], 'fields': ['pos_config_ids', 'queue_order', 'pos_category_ids', 'url', 'ip_address']}}

    def _get_pos_ui_pos_kitchen_screen_config(self, params):
        return self.env['pos.kitchen.screen.config'].search_read(**params['search_params'])

    def _loader_params_pos_order_line(self):
        return {'search_params': {'domain': [], 'fields': ['product_id', 'order_id', 'qty',]}}

    def _get_pos_ui_pos_order_line(self, params):
        return self.env['pos.order.line'].search_read(**params['search_params'])

    def _loader_params_pos_order(self):
        return {'search_params': {'domain': [], 'fields': ['id', 'name', 'date_order', 'order_progress', 'partner_id', 'lines', 'pos_reference', 'kitchen_order_name',]}}

    def _get_pos_ui_pos_order(self, params):
        return self.env['pos.order'].search_read(**params['search_params'])

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model = ['pos.kitchen.screen.config',
                     'pos.order.line', 'pos.order']
        for models in new_model:
            if (models not in result):
                result.append(models)
        return result

    def _loader_params_pos_order_line(self):
        pos_screen_data = self.env['pos.kitchen.screen.config'].search([])
        validation_date = datetime.date.today()
        if (pos_screen_data):
            pos_categ_ids = []
            for data in pos_screen_data:
                pos_categ_ids.extend(data.pos_category_ids.ids)
            return {
                'search_params': {
                    'domain': [('product_id.pos_categ_ids', 'in', pos_categ_ids), ('order_id.date_order', '>=', validation_date), ('order_id.session_id', '=', self.name), ('order_id.state', 'not in', ['draft', 'cancel', False]), ('order_id.order_progress', '!=', False)],
                    'fields': [],
                },
            }
        else:
            return {
                'search_params': {
                    'domain': [('order_id.session_id', '=', self.name), ('order_id.state', 'not in', ['draft', 'cancel', False])],
                    'fields': [],
                },
            }

    def _loader_params_pos_order(self):
        order_line_id = self.env['pos.kitchen.orderline'].search([])
        order = []
        for order_line in order_line_id:
            order.extend([order_line.order_id.id])
        return {
            'search_params': {
                'domain': [('id', 'in', order), ('kitchen_order_name', '!=', False)],
                'fields': [],
            },
        }

    def get_formatted_channel_name(self, db_name, config_id=1, channel='_wk_pos_kitchen_poll'):
        return '{}_{}'.format(channel, config_id)
       
    def _notify_changes_in_kitchen(self, records, config_id,model_name='pos.kitchen.order', first=False):
        """ 
            Sends the changes through the bus of related orders in the pos
            params:
            records:list of orders
            first:boolean
            is_create: boolean
        """
        notifications = []
        channel = self.get_formatted_channel_name(self.env.cr.dbname)
        if first:
            notifications.append([channel, "websocket_status", []])
        else:
            data = [{'data': rec.read(),'model_name': model_name} for rec in records]
            notifications.append([channel, "pos_kitchen_data_update", data])
        if len(notifications) > 0:
            self.env['bus.bus']._sendmany(notifications)
