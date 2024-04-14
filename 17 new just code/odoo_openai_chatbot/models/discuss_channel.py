# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from pickle import FALSE
from odoo import api, fields, models, _, SUPERUSER_ID, tools
from odoo.tools import email_normalize, html2plaintext, is_html_empty, plaintext2html
import logging
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class MailChannel(models.Model):

    _inherit = 'discuss.channel'

    is_connected_with_agent = fields.Boolean('Is connected with agent')
    is_connected_with_ai_bot = fields.Boolean('Is connected with AiBot')
    first_response = fields.Boolean('First Response', default=True)
    is_welcome_msg_sent = fields.Boolean("AI Bot Welcome Msg Status")
    ai_bot_config_id = fields.Many2one("ai.bot.config", string="Ai Bot Config")

    @api.onchange('is_connected_with_ai_bot')
    def reset_bot_config(self):
        if not self.is_connected_with_ai_bot and self.ai_bot_config_id:
            self.ai_bot_config_id = False

    def get_ai_answers(self, query, ai_config):
        connection_info = ai_config._get_connection_info()
        collection_name = ai_config.get_collection_name()
        kwargs = {
            'model_name': ai_config.selected_ai_model,
            'temprature': ai_config.temprature,
            'max_tokens': ai_config.max_tokens,
        }
        res = ai_config._openai_setup().chatbot(query, connection_info,
                      collection_name, **kwargs)
        if res[0]:
            return res[1]
        else:
            return False

    def connect_ai_chat_bot(self, uuid, author_id, email_from, ai_bot_config_id):
        if ai_bot_config_id and not self.is_connected_with_ai_bot:
            self.write({
                'is_welcome_msg_sent': True,
                'is_connected_with_ai_bot': True,
                'ai_bot_config_id': ai_bot_config_id.id
            })

        res = self.get_ai_answers(self._context.get(
            'res_message', ''), ai_bot_config_id)
        if res:
            message = self.with_context(mail_create_nosubscribe=True, from_bot=True).message_post(
                author_id=author_id,
                email_from=email_from,
                body=plaintext2html(res),
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
            )
            return message
        else:
            return self.connect_with_agent(uuid, author_id)

    def connect_with_agent(self, uuid, author_id):
        self.write({
            'is_connected_with_agent': True,
            'is_connected_with_ai_bot': False
        })
        available = self.livechat_channel_id.with_context(uuid=uuid)._get_operator()
        if available:
            try:
                self._broadcast([available.partner_id.id])

                self.add_members(available.partner_id.id)
                return True
            except Exception as e:
                _logger.info(
                    "-----<Connect with agent : Exception>---%r------", str(e))
                return False
        else:
            return False

    def _send_bot_response(self, uuid, bot_action_id=False):
        author = self.livechat_channel_id.bot_user_id.partner_id
        author_id = author.id
        email_from = author.email_formatted
        ai_bot_config_id = self.livechat_channel_id.ai_bot_config_id
        if not self.is_connected_with_agent and self._context.get('res_message', '') != self.livechat_channel_id.shortcut_to_connect_agent and ai_bot_config_id.state == 'trained':
            return self.connect_ai_chat_bot(uuid, author_id, email_from, ai_bot_config_id)
        else:
            return self.connect_with_agent(uuid, author_id)


    def _get_visitor_leave_message(self, operator=False, cancel=False):
        message = super(MailChannel, self)._get_visitor_leave_message(
            operator, cancel)
        name = _(
            'The visitor') if not self.livechat_visitor_id else self.livechat_visitor_id.display_name
        if cancel and self.livechat_channel_id.is_bot_enable and self.is_connected_with_agent:
            message = _("""%s has started a conversation with %s. 
                        Hi, How may i help you?.""") % (name, operator or _('an operator'))
        return message

    def _close_livechat_session(self, **kwargs):
        """ Set deactivate the livechat channel and notify (the operator) the reason of closing the session."""
        self.ensure_one()
        if self.channel_type == 'livechat' and self.livechat_active and self.is_connected_with_ai_bot:
            self.is_connected_with_ai_bot = False
        return super(MailChannel, self)._close_livechat_session(**kwargs)
