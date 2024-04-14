# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


MODEL_OPTIONS = [
    ('gpt-4', 'GPT-4'),
    ('gpt-4-1106-preview', 'GPT-4 Turbo'),
    ('gpt-3.5-turbo', 'GPT-3.5 TURBO'),
    ('gpt-3.5-turbo-1106', 'Updated GPT-3.5 TURBO'),
]

TYPE_OPTIONS = [
    ('odoo', 'Odoo Builtin API (FREE)'),
    ('openai', 'OpenAI API with my own key')
]

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    openai_api_type = fields.Selection(TYPE_OPTIONS, config_parameter='web_editor_ai.api_type', required=True)
    openai_api_key = fields.Char("OpenAI API key", default="odoo", config_parameter='web_editor_ai.api_key')
    openai_model = fields.Selection(MODEL_OPTIONS, default=MODEL_OPTIONS[0][0], config_parameter='web_editor_ai.model', required=True)

    def action_open_content_generator_options(self):
        return {
            'name': _('Content Generator Option'),
            'type': 'ir.actions.act_window',
            'res_model': 'content.generator.options',
            'view_mode': 'tree',
            'domain': [],
        }

