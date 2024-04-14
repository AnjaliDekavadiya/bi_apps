# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###############################################################################


from odoo import api, models, fields
from odoo.exceptions import ValidationError 
import requests
import json

import logging
_logger = logging.getLogger(__name__)



class OpenAiConfiguration(models.Model):
    _name = "open.ai.configuration"
    _description = 'OPENAI Configuration'
    

    def get_ai_engine_header(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('wk_chatgpt_engine.api_key')
        header = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
        }
        return header

    
    """OPEN AI Model Lists"""
    def get_model_lists(self):
        url = "https://api.openai.com/v1/models"
        payload={}  
        headers = self.get_ai_engine_header()
        response = requests.request("GET", url, headers=headers, data=payload).content
        response = json.loads(response)
        return response

    
    def parse_response(self, response):
        res = {
            'status': True,
            'message': 'Success',
            'content': ''
        }
        if response.get('error'):
            res['status'] = False
            res['message'] = response.get('error').get('message')
        elif response.get('id'):
            content = response['choices'][0]['message']['content']
            res['content'] = content
        else:
            res['status'] = False
            res['message'] = "Bad Payload"      
        return res
     
    """ OpenAi Payload"""
    def openai_payload(self, prompt="", max_token=3500, temperature=1, ai_model=""):
        payload = dict()
        payload["model"] = ai_model or 'gpt-3.5-turbo'
        payload["messages"] = prompt
        payload["max_tokens"] = max_token
        payload["temperature"] =  temperature or 1
        payload["top_p"] =  1
        return payload

 
    """OPEN AI Generate Content"""
    def get_generate_content(self, final_prompt, max_token, temperature, ai_model):
        url = "https://api.openai.com/v1/chat/completions"
        if self.env.context.get('bulk_updates'):
            payload = self.openai_payload(final_prompt, max_token, temperature, ai_model)
        else:
            payload = self.openai_payload(final_prompt, max_token, temperature, ai_model)
        payload = payload
        payload = json.dumps(payload)
        headers = self.get_ai_engine_header()
        response = requests.request("POST", url, headers=headers, data=payload).content
        response = json.loads(response)
        response = self.parse_response(response)
        return response
    

    # """ Grammar Correction Payload"""
    # def get_grammar_payload(self, prompt="", temperature=1, ai_model=""):
    #     payload = dict()
    #     payload["model"] = ai_model or 'gpt-3.5-turbo'
    #     payload["messages"] = [
    #         {
    #             "role": "user",
    #             "content": f"{prompt}"
    #         }
    #     ]
    #     payload["max_tokens"] = 3500
    #     payload["temperature"] =  temperature or 1
    #     payload["top_p"] =  1
    #     payload["frequency_penalty"] =  0
    #     payload["presence_penalty"] =  0
    #     return payload
    
    """OPEN AI Grammar Correction """
    def get_grammar_content(self, prompt, temperature, ai_model):
        url = "https://api.openai.com/v1/chat/completions"
        max_tokens = 3500
        payload = self.openai_payload(prompt, max_tokens, temperature, ai_model)
        payload = json.dumps(payload)
        headers = self.get_ai_engine_header()
        response = requests.request("POST", url, headers=headers, data=payload).content
        response = json.loads(response)
        response = self.parse_response(response)
        return response
    

    # """Translation Payload"""
    # def get_translate_payload(self, prompt="", temperature=1, ai_model=""):
    #     payload = dict()
    #     payload["model"] = ai_model or 'gpt-3.5-turbo'
    #     payload["messages"] = [
    #         {
    #             "role": "user",
    #             "content": f"{prompt}"
    #         }
    #     ]
    #     payload["max_tokens"] = 3500
    #     payload["temperature"] =  temperature or 1
    #     payload["top_p"] =  1
    #     payload["frequency_penalty"] =  0
    #     payload["presence_penalty"] =  0
    #     return payload
    

    """OPEN AI Translation """
    def get_translate_content(self, prompt, temperature, ai_model):
        url = "https://api.openai.com/v1/chat/completions"
        max_tokens = 3500
        payload = self.openai_payload(prompt, max_tokens, temperature, ai_model)
        payload = json.dumps(payload)
        headers = self.get_ai_engine_header()
        response = requests.request("POST", url, headers=headers, data=payload).content
        response = json.loads(response)
        response = self.parse_response(response)
        return response
    

    """SEO Payload"""
    def suggest_seo_payload(self, prompt="", temperature=1, ai_model=""):
        payload = dict()
        payload["model"] = ai_model  or 'gpt-3.5-turbo'
        payload["messages"] = [
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ]
        payload["max_tokens"] = 3500
        payload["temperature"] =  temperature or 1
        payload["top_p"] =  1
        payload["frequency_penalty"] =  0
        payload["presence_penalty"] =  0
        return payload  
    


    """ SEO """
    def suggest_seo_content(self, prompt, temperature, ai_model):
        url = "https://api.openai.com/v1/chat/completions"
        payload = self.suggest_seo_payload(prompt, temperature, ai_model)
        payload = json.dumps(payload)
        headers = self.get_ai_engine_header()
        response = requests.request("POST", url, headers=headers, data=payload).content
        response = json.loads(response)
        response = self.parse_response(response)
        return response

      

    """ SEO Bulk Update"""
    def seo_bulk_update(self, prompt, temperature=1, ai_model=""):
        url = "https://api.openai.com/v1/chat/completions"
        payload = self.suggest_seo_payload(prompt, temperature, ai_model)
        payload = json.dumps(payload)
        headers = self.get_ai_engine_header()
        response = requests.request("POST", url, headers=headers, data=payload).content
        response = json.loads(response)
        response = self.parse_response(response)
        return response
      
    

    
    
    




