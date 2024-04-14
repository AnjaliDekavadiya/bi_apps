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

_logger = logging.getLogger(__name__)

class AiGrammarWizard(models.TransientModel):
    _name = "ai.grammar.wizard"
    _description = "AI Grammar Wizard"




    def _get_default_content(self):
        if self.env.context.get('active_content'):
            return  html2plaintext(self.env.context.get("active_content"))


    content_preview = fields.Text(string="Preview")
    content =  fields.Text(string="Content", default=_get_default_content,)
    content_description =  fields.Text(string="Content Description")



    @api.model
    def _active_model(self):
        active_model_name = self.env.context.get('active_model_name')
        active_model_id = self.env.context.get('active_model_id')
        active_model = self.env[active_model_name].browse(active_model_id)
        return active_model
    
    @api.model
    def process_grammar_content(self, prompt, *args, **kwargs):
        model_name = kwargs.get('model')
        default_content = prompt
        chosen_lang =  kwargs.get("lang")
        lang = self.env["res.lang"].sudo().search([('code', '=', chosen_lang)])
        
        prompt_instruction = self.env['openai.prompt.instruction'].search([('model_id', '=', model_name)], limit=1)
        temperature = prompt_instruction.temperature if prompt_instruction else 0.5
        ai_model = prompt_instruction.openai_model
        
        if not chosen_lang:
            raise UserError("Please Choose at least 1 Language")
        if not default_content:
            raise UserError("Please Enter the text for grammar Correction")
        prompt = [
            {'role': 'system', 'content': f'You will be provided with statements, and your task is to correct them to {lang.name}.'},
            {'role': 'user', 'content': f'{default_content}'}
        ]
        response = self.env['open.ai.configuration'].search([], limit=1).get_grammar_content(prompt, temperature, ai_model)
        if not response.get('status'):
                raise UserError(response.get('message'))
        else:
            return response.get('content')


