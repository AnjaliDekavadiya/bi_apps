# -*- coding: utf-8 -*-
##########################################################################
#
# Copyright (c) 2020-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import models, fields, api
from ..walmart_api import WalmartConnect

import json
import logging
_logger = logging.getLogger(__name__)


class WalmartFeedStatus(models.TransientModel):

    _name = "walmart.feed"
    _description = "Walmart Feed"

    feed_id = fields.Char("Feed ID")
    channel_id = fields.Many2one(
        "multi.channel.sale", "Walmart Instance")

    def check_feed_status(self):
        channel_vals = self.channel_id.read([
            "environment",
            "walmart_client_id",
            "walmart_client_secret",
            "walmart_marketplace",
            "walmart_access_token",
            "walmart_channel_type",
        ])[0]

        if channel_vals.get("environment") == "production":
            production = True
            sandbox = False
        else:
            production = False
            sandbox = True

        with WalmartConnect(channel_vals["walmart_client_id"], channel_vals["walmart_client_secret"], self.channel_id,
                            channel_vals["walmart_access_token"], channel_vals["walmart_channel_type"],
                            channel_vals["walmart_marketplace"], sandbox, production) as Connect:
            msg = ''
            if Connect.marketplace != "CA":
                Connect.checkTokenExpiry() #If token is expired it will update it too

            result = Connect.getResponse(
                f"feeds/{self.feed_id}?includeDetails=true")
            if result["data"]:
                msg = json.dumps(result["data"], indent=4)
            if not msg:
                msg = 'Feed-ID (<b>%s</b>) does not exists.' % (self.feed_id)
            return self.channel_id.display_message(msg.replace('\n', '</br>').replace(' ', '&nbsp;'))
