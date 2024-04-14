# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
import logging
_logger = logging.getLogger(__name__)

from odoo.http import Controller, route, request
from odoo.addons.walmart_odoo_connector.walmart_api import WalmartConnect

class WalmartController(Controller):
    @route(['/channel/walmart/<int:id>/realtime_ok',], auth="public", type='json')
    def recieve_order_CreateEvent(self, id, **order_info):
        _logger.info("~~~~~~~~~~~~ Test WalmartRealtime Order Sync Successfull ~~~~~~~~~~~~~~")
        if order_info:

            channel_id = request.env['multi.channel.sale'].browse(int(id))
            if channel_id.environment == "production":
                production = True
                sandbox = False
            else:
                production = False
                sandbox = True
            martketplace = channel_id.walmart_marketplace
            with WalmartConnect(channel_id.walmart_client_id, channel_id.walmart_client_secret, channel_id, channel_id.walmart_access_token,
                channel_id.walmart_channel_type, martketplace, sandbox, production) as Connect:
                    Connect.checkTokenExpiry()
                    store_order_id = order_info.get("payload",{}).get("purchaseOrderId")
                    order_list, _ = Connect.getOrders(filter_type="id", object_id=store_order_id)
                    try:
                        result = channel_id.sync_order_feeds(order_list)
                    except Exception as e:
                        _logger.info("~~~~~~~~~~ Real-time Order Evaluation Error ~~~~~~~~~~~(%r)",e)
                    else:
                        _logger.info("~~~~~~~~~~ Real-time Order Evaluation Result ~~~~~~~~~~~(%r)",result['message'])

        return True
