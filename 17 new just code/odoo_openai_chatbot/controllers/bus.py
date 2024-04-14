# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import SUPERUSER_ID, tools
from odoo.http import request, route
from odoo.addons.mail.controllers.mail import MailController

import logging

_logger = logging.getLogger(__name__)

class MailChatControllerInherit(MailController):
    
    @route('/mail/bot/response', type="json", auth="public", cors="*")
    def mail_chat_bot_response(self, uuid, message_content, **kwargs):
        response = {
            'status': True,
        }
        mail_channel = request.env["discuss.channel"].sudo().search(
            [('uuid', '=', uuid)], limit=1)
        if not mail_channel:
            return False
        if mail_channel.livechat_channel_id.is_bot_enable and mail_channel.livechat_channel_id.bot_user_id and not mail_channel.is_connected_with_agent:
            mail_channel.with_context(
                res_message=message_content)._send_bot_response(uuid)
        if mail_channel.is_connected_with_agent or mail_channel.livechat_channel_id.shortcut_to_connect_agent == str(message_content):
            response.update({
                'connected_with_agent': True
            })
        return response
