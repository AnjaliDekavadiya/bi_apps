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




class AiContentWizard(models.TransientModel):
    _name = "ai.content.wizard"
    _description = "AI Content Wizard"
    

    
    def find_prompt_instruction(self):
        active_model_name = self.env.context.get('active_model_name')
        prompt_instruct = self.env['openai.prompt.instruction'].search([('model_id', '=', active_model_name)], limit=1)
        return prompt_instruct

    def _get_tone_domain(self):
        active_model = self.env.context.get('active_model_name')
        if active_model:
            prompt_instruct = self.find_prompt_instruction()
            return [('id', 'in', prompt_instruct.tone_ids.ids)] if prompt_instruct else []
        
        return [('visibility', '=', 'global')]
         
      
    def _get_maximum_token(self):
        prompt_instruct = self.find_prompt_instruction()
        return prompt_instruct.content_length if prompt_instruct else 250
        

    def _default_tone(self):
        prompt_instruct = self.find_prompt_instruction()
        return prompt_instruct.tone_ids[0].id if prompt_instruct and prompt_instruct.tone_ids else False
        
        
    max_token = fields.Integer(string="Maximum Content length", default=_get_maximum_token, help="Choose the length of the AI Content.")
    prompt = fields.Text(string="Prompt")
    content_description = fields.Text(string="Description")
    tone_id = fields.Many2one(comodel_name='openai.prompt.tone', domain =_get_tone_domain, default=lambda self: self._default_tone())



    @api.model
    def _active_model(self,model_id, model_name):
        active_model = model_name
        active_model_id = model_id
        if active_model_id:
            active_model = self.env[active_model].browse(active_model_id)
            return active_model
        else:
            return ""
    
     
    @api.model
    def get_tone(self, *args, **kwargs):
        model_id = kwargs.get('id')
        model_name = kwargs.get('model')
        model = self._active_model(model_id, model_name)
        prompt_instruction = self.env['openai.prompt.instruction'].search([('model_id', '=', model_name)], limit=1)
        prompt_tone = self.env['openai.prompt.tone'].search([('visibility', '=', 'global')])
        if model and prompt_instruction:
            result = prompt_instruction.tone_ids.read(['name'])
            return result
        else:
            return prompt_tone.read(['name'])
          
        
    
    @api.model
    def change_tone(self, *args, **kwargs):
        model_id = kwargs.get('id')
        model_name = kwargs.get('model')
        tone = kwargs.get('tone')
        model = self._active_model(model_id, model_name)
        prompt_instruction = self.env['openai.prompt.instruction'].search([('model_id', '=', model_name)], limit=1)
        prompt_tone = self.env['openai.prompt.tone'].search([('id', '=', tone)])
        suffixes = ""

        if model and prompt_instruction.model_field_ids:
            for field in prompt_instruction.model_field_ids:
                if field.ttype == 'many2one':
                    value = model[0][field.name].name
                    if value:
                        suffixes += f"{field.field_description}: {value}\n"
                elif field.ttype == 'one2many':
                    if field.name == 'attribute_line_ids':
                        values = model[0][field.name]
                        for value in values:
                            key = value.attribute_id.name
                            pair = value.value_ids.mapped("name")
                            result = ", ".join(pair)
                            suffixes += f"{key}: {result}\n"
                    elif field.name == 'product_template_variant_value_ids': 
                        values = model[0][field.name]

                elif field.ttype == 'many2many':
                    values = model[0][field.name].mapped("name")
                    value = ", ".join(values)
                    if value:
                        suffixes += f"{field.field_description}: {value}\n"
                elif field.ttype in ['char', 'text', 'html', 'integer', 'float'] and field.name in model[0]:
                    value = model[0][field.name]
                    if value:
                        suffixes += f"{field.field_description}: {value}\n"
                        
            result = f'{prompt_tone.content_style} using the following product details to summarise your description:\n{suffixes}'
            return result
        else:
            result = f'{prompt_tone.content_style}'
            return result
        
        
        
        
    @api.model
    def get_odooapi_key(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('wk_chatgpt_engine.api_key_action')
        if api_key == 'odoo_api_key':
            return True
        else:
            return False
        
    @api.model
    def get_content_length(self, *args, **kwargs):
        model_id = kwargs.get('id')
        model_name = kwargs.get('model')
        
        prompt_instruction = self.env['openai.prompt.instruction'].search([('model_id', '=', model_name)], limit=1)
        
        return prompt_instruction.content_length if prompt_instruction else 200
       
        
    @api.model
    def get_prompt(self, *args, **kwargs):
        model_id = kwargs.get('id')
        model_name = kwargs.get('model')
        
        model = self._active_model(model_id, model_name)
        prompt_instruction = self.env['openai.prompt.instruction'].search([('model_id', '=', model_name)], limit=1)
        suffixes = ""

        if model and prompt_instruction.model_field_ids:
            for field in prompt_instruction.model_field_ids:
                if field.ttype == 'many2one':
                    value = model[0][field.name].name
                    if value:
                        suffixes += f"{field.field_description}: {value}\n"
                elif field.ttype == 'one2many':
                    if field.name == 'attribute_line_ids':
                        values = model[0][field.name]
                        for value in values:
                            key = value.attribute_id.name
                            pair = value.value_ids.mapped("name")
                            result = ", ".join(pair)
                            suffixes += f"{key}: {result}\n"
                    elif field.name == 'product_template_variant_value_ids': 
                        values = model[0][field.name]

                elif field.ttype == 'many2many':
                    values = model[0][field.name].mapped("name")
                    value = ", ".join(values)
                    if value:
                        suffixes += f"{field.field_description}: {value}\n"
                elif field.ttype in ['char', 'text', 'html', 'integer', 'float'] and field.name in model[0]:
                    value = model[0][field.name]
                    if value:
                        suffixes += f"{field.field_description}: {value}\n"
                        
            result = f' Write a Product Description in a Professional manner using the following product details to summarise your description:\n{suffixes}'
            prompt = result
            return prompt
             

    @api.model
    def process_ai_content(self, prompt, *args, **kwargs):
        model_name = kwargs.get('model')
        tone_length = kwargs.get('toneLength')
        
        prompt_instruction = self.env['openai.prompt.instruction'].search([('model_id', '=', model_name)], limit=1)
        
        temperature = prompt_instruction.temperature if prompt_instruction else 0.5
        ai_model = prompt_instruction.openai_model if prompt_instruction else None
        max_token = tone_length or (prompt_instruction.content_length if prompt_instruction else 200)
        prompt = [
            {'role': 'system', 'content': f'You will be provided with statements, and your task is to generate a content.'},
            {'role': 'user', 'content': f'{prompt}'}
        ]
        configuration = self.env['open.ai.configuration'].search([], limit=1)
        response = configuration.get_generate_content(prompt, max_token, temperature, ai_model)
        
        if not response.get('status'):
            raise UserError(response.get('message'))
        else:
            return response.get('content')

