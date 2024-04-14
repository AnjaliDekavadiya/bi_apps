# -*- coding: utf-8 -*-
from odoo import api, Command, fields, models, _, release
from odoo.exceptions import ValidationError, UserError
from odoo.addons.iap.tools import iap_tools
import openai
import logging
_logger = logging.getLogger(__name__)

DEFAULT_OLG_ENDPOINT = 'https://olg.api.odoo.com'

class AiApi(models.Model):
    _name = 'ai.api'
    _description = 'OpenAI API'

    @api.model
    def make_ai_request(self, system, prompt):
        if self.env['ir.config_parameter'].sudo().get_param('web_editor_ai.api_type') == 'openai':
            return self._make_openai_request(system, prompt)
        else:
            return self._make_iap_request(system, prompt)

    @api.model
    def correct_text(self, text):
        system = 'Check the text for grammar mistakes. Respond only with the revised text without any comments.'
        return self.make_ai_request(system, text)

    @api.model
    def translate_text(self, text):
        language = self.env.lang
        system = f'Translate the provided text to {language}. Respond only with the translation.'
        return self.make_ai_request(system, text)

    @api.model
    def generate_content(self, data):
        about = data.get('about', '')
        tone = data.get('tone', '')
        text_format = data.get('format', '')
        length = data.get('length', '')

        text_format = '' if text_format == 'Other' else f'Format: {text_format}.\n'
        tone = '' if tone == 'Other' else f'Tone: {tone}.\n'
        length = '' if length == 'Other' else f'Length: {length}.\n'

        system = """You are a content generator. Generate content about given subject or according to instructions\n"""
        system += f"{text_format} {length} {tone}\n"
        system += """Format the response as a block of HTML code inside a div tag. 
        Respond only with the content without your comments. 
        Also do not include the ```html tags"""

        return self.make_ai_request(system, about)

    @api.model
    def vanilla_request(self, prompt):
        system = """You are an helpful assistant.
        Format the response as a block of HTML code inside a div tag. 
        Respond only with the content without your comments. 
        Also do not include the ```html tags"""

        return self.make_ai_request(system, prompt)

    def _make_openai_request(self, system, prompt):
        openai.api_key = self.env['ir.config_parameter'].sudo().get_param('web_editor_ai.api_key')
        model = self.env['ir.config_parameter'].sudo().get_param('web_editor_ai.model')

        try:
            response = openai.chat.completions.create(
                model=model,
                temperature=1,
                max_tokens=3000,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as error:
            raise ValidationError(error)

    def _make_iap_request(self, system, prompt):
        try:
            conversation_history = [{'role': 'system', 'content': system}]

            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            olg_api_endpoint = IrConfigParameter.get_param('web_editor.olg_api_endpoint', DEFAULT_OLG_ENDPOINT)
            response = iap_tools.iap_jsonrpc(olg_api_endpoint + "/api/olg/1/chat", params={
                'prompt': prompt,
                'conversation_history': conversation_history,
                'version': release.version,
            })

            if response['status'] == 'success':
                return response['content']
            elif response['status'] == 'error_prompt_too_long':
                raise UserError(_("Sorry, your prompt is too long. Try to say it in fewer words."))
            else:
                raise UserError(_("Sorry, we could not generate a response. Please try again later."))
        except Exception as error:
            raise ValidationError(error)

