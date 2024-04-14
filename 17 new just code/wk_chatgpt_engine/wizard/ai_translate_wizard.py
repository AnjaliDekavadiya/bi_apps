# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###############################################################################


from odoo import api, models, fields
from odoo.exceptions import UserError 
from odoo.tools import html2plaintext
import logging
import re
from odoo.addons.web_editor.controllers.main import Web_Editor

_logger = logging.getLogger(__name__)

class AiTranslateWizard(models.TransientModel):
    _name = "ai.translate.wizard"
    _description = "AI Translate Wizard"




    def _get_default_content(self):
        if self.env.context.get('active_content'):
            return  html2plaintext(self.env.context.get("active_content"))


    translate_lang_ids = fields.Many2many(comodel_name="res.lang", relation="ai_translate_lang_rel", string="Language")
    content =  fields.Text(string="Content", default=_get_default_content,)


    @api.model
    def _active_model(self):
        active_model_name = self.env.context.get('active_model_name')
        active_model_id = self.env.context.get('active_model_id')
        active_model = self.env[active_model_name].browse(active_model_id)
        return active_model
    
    

    def process_translate_content(self):
        model = self._active_model()
        content_prompt = self.content
        chosen_lang = self.translate_lang_ids
        active_field = self.env.context.get('active_field')
        
        if not chosen_lang:
            raise UserError("Please Choose at least 1 Language")
        
        if not content_prompt:
            raise UserError("Please Enter the text for Translation")

        result = model.get_field_translations(active_field, langs=None)
        odoo_api_key = self.env['ir.config_parameter'].sudo().get_param('wk_chatgpt_engine.api_key_action')
        
        model_name = self.env.context.get('active_model_name')
        prompt_instruction = self.env['openai.prompt.instruction'].search([('model_id', '=', model_name)], limit=1)
        temperature = prompt_instruction.temperature if prompt_instruction else 0.5
        ai_model = prompt_instruction.openai_model

        final_dict = {}
        output = {}

        for lang in chosen_lang:
            if odoo_api_key == 'openai_api_key':
                prompt = [
                    {'role': 'system', 'content': f'You will be provided with a sentence, and your task is to translate it into  {lang.name}.'},
                    {'role': 'user', 'content': f'{content_prompt}'}
                ]
                response = self.env['open.ai.configuration'].search([], limit=1).get_translate_content(prompt, temperature, ai_model)
                self._handle_translation_response(response, lang.code, result, content_prompt, output, final_dict)
            else:
                conversation_history = [
                    {'role': 'system', 'content': f'You will be provided with statements, and your task is to convert them to {lang.name}.'},
                    {'role': 'assistant', 'content': 'What do you need ?'},
                    {'role': 'user', 'content': f'{content_prompt}'}
                ]
                response = Web_Editor.generate_text(self, content_prompt, conversation_history)
                for item in result[0]:
                    if item['lang'] == lang.code:
                        output[lang.code] = {item['value'] or item['source'] : html2plaintext(response)}
                        final_dict.update(output)

        result = model.update_field_translations(active_field, final_dict)
        return {'type': 'ir.actions.act_window_close'}

    def _handle_translation_response(self, response, lang_code, result, content_prompt, output, final_dict):
        if not response.get('status'):
            raise UserError(response.get('message'))

        for item in result[0]:
            if item['lang'] == lang_code:
                output[lang_code] = {item['value'] or item['source']: html2plaintext(response['content'])}
                final_dict.update(output)