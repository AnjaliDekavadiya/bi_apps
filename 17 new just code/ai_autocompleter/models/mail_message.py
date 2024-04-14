import openai
import logging
from odoo import _, fields, models, tools

_logger = logging.getLogger(__name__)


class Message(models.Model):
    _inherit = "mail.message"

    def ai_reply_message(self):
        message_body = tools.html2plaintext(self.body)        
        config_parameter = self.env['ir.config_parameter'].sudo()
        openai.api_key = config_parameter.get_param('openai_api_key')
        engine = config_parameter.get_param('openai_api_engine')
        max_tokens = config_parameter.get_param('openai_api_max_tokens')
        response_AI = ''
        try:
            prompt = "Reply to this message like a human would:\n\n" + message_body + "\n\nReply:"
            #('gpt-3.5-turbo', 'GPT-3.5 Turbo'),        ('gpt-4', 'GPT-4'),        ('gpt-4-32k', 'GPT-4 32k'),
            if engine in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-32k']:
                response = openai.ChatCompletion.create(
                    model=engine,
                    messages = [{'role': 'user', 'content': prompt}],
                    max_tokens=int(max_tokens),
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                response_AI= response.choices[0].message.content
            else:
                response = openai.Completion.create(
                    engine=engine,
                    prompt=prompt,
                    max_tokens=int(max_tokens),
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                response_AI= response.choices[0].text.strip()
            return response_AI
        except Exception as e:
            return "Configure your OpenAI API key in Settings > General Settings > OpenAI API Key and try again." + str(
                e)
