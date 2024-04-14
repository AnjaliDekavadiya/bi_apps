# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models
from ..ai_chat.openai_chatbot import AiChatBot


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openai_api_key = fields.Char(
        string="Api Key",
        config_parameter='odoo_openai_chatbot.openai_api_key',
    )

    ai_models = fields.Char(
        "Ai Models", config_parameter='odoo_openai_chatbot.ai_models',)
    
    def _openai_setup(self):
        client = AiChatBot(
            api_key = self.openai_api_key
        )
        return client

    def set_values(self):
        super().set_values()
        if self.openai_api_key:
            self.ai_models = str(self._openai_setup()._get_model_list())
            self.env['ir.config_parameter'].sudo().set_param(
                'odoo_openai_chatbot.ai_models', self.ai_models)
        else:
            self.env['ir.config_parameter'].sudo().set_param(
                'odoo_openai_chatbot.ai_models', '')
