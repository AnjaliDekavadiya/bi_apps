# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################


from odoo import fields, models, _

import logging


_logger = logging.getLogger(__name__)


class WkImLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    is_bot_enable = fields.Boolean('Is Bot Enable')
    bot_user_id = fields.Many2one('res.users')
    # bot_template_id = fields.Many2one('bot.templates')
    ai_bot_config_id = fields.Many2one("ai.bot.config", string="Bot")
    shortcut_to_connect_agent = fields.Char(
        'Shortcut To Connect agent', help="Connect with agent if dont want the respose from the bot.", default="\c")
    
    
    
    def _compute_available_operator_ids(self):
        for record in self:
            if record.is_bot_enable and not record._return_channel_status():
                record.bot_user_id.im_status = 'online'
                record.available_operator_ids = record.bot_user_id
            else:
                record.available_operator_ids = record.user_ids.filtered(lambda user: user.im_status == 'online')


    def _return_channel_status(self):
        status = False
        # todo improve logic to get current active channel
        if self._context.get('uuid', False):
            mail_channel = self.env["discuss.channel"].sudo().search(
                [('uuid', '=', self._context['uuid'])], limit=1)
            if mail_channel and mail_channel.is_connected_with_agent:
                status = True
        else:
            info = self.env['website'].get_current_website(
            )._get_livechat_request_session()
            if info.get('uuid'):
                mail_channel = self.env["discuss.channel"].sudo().search(
                    [('uuid', '=', info['uuid'])], limit=1)
                if mail_channel and mail_channel.is_connected_with_agent:
                    status = True
        return status

    def action_set_boot_options(self):
        self.write({
            'is_bot_enable': True,
            'bot_user_id': self.env.ref('odoo_openai_chatbot.user_bot').id if self.env.ref('odoo_openai_chatbot.user_bot') else False,
            'ai_bot_config_id': self.env.ref('odoo_openai_chatbot.default_ai_bot').id if self.env.ref('odoo_openai_chatbot.default_ai_bot') else False
        })
