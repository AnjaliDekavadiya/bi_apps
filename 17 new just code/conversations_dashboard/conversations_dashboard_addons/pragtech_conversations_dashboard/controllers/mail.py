# Copyright 2021 Ivan Yelizariev <https://twitter.com/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

from odoo.addons.mail.controllers.webclient import WebclientController


class MultiLivechatMailController(WebclientController):
    @http.route()
    def mail_init_messaging(self):
        values = super().mail_init_messaging()
        channels_data = request.env["discuss.channel"].get_channels()
        _logger.info("these are the values from init msg %s: ", str(values["channels"]))
        for channels in channels_data:
            values["channels"].append(channels)
        values["multi_livechat"] = request.env["discuss.channel"].multi_livechat_info()
        _logger.info("these are the values from init msg %s: ", str(values["channels"]))
        return values
