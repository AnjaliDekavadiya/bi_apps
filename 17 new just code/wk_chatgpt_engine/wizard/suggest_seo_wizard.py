# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###############################################################################


from odoo import api, models, fields
from odoo.exceptions import UserError 
from odoo.tools import html2plaintext
from odoo.addons.web_editor.controllers.main import Web_Editor

import logging

_logger = logging.getLogger(__name__)


class SuggestSeoWizard(models.TransientModel):
    _name = "suggest.seo.wizard"
    _description = "Suggest Seo Wizard"
    
    

    @api.model
    def _active_model(self):
        active_model_name = self.env.context.get('model_active')
        product_id = self.env.context.get('product')
        
        if active_model_name and product_id:
            active_model = self.env[active_model_name].browse(product_id)
            return active_model
        else:
            return False
    
    
    @api.onchange('tone_id')
    def _onchange_prompt(self):
        model = self._active_model()
        suggest_seo = self.env['openai.suggest.seo'].search([('model_id', '=', self.env.context.get('active_model'))], limit=1)
        suffixes = ""

        if model and self.tone_id and suggest_seo.model_field_ids:
            for field in suggest_seo.model_field_ids:
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

            if self.tone_id.content_style:
                result = f' {self.tone_id.content_style}:\n{suffixes}'
                self.prompt = result
            else:
                self.prompt = ""

        
    def find_suggest_seo(self):
        model_active = self.env.context.get('model_active')      
        if model_active:
            suggest_seo = self.env['openai.suggest.seo'].sudo().search([('model_id', '=', model_active)], limit=1)
            return suggest_seo
        return False

           
    def _get_tone_domain(self):
        context = self.env.context
        if context.get('model_active'):
            suggest_seo = self.find_suggest_seo()
            if suggest_seo:
                return [('id', 'in', suggest_seo.tone_ids.ids)]
        return [('visibility', '=', 'global')]
        
    def _default_tone(self):
        suggest_seo = self.find_suggest_seo()
        return suggest_seo.tone_ids[0].id if suggest_seo and suggest_seo.tone_ids else False

    
    
    prompt = fields.Text(string="Prompt")
    content_preview = fields.Text(string="Preview")
    meta_description = fields.Text(string="Meta-Description")
    meta_title = fields.Text(string="Meta-Title")
    meta_keywords = fields.Text(string="Meta-Keywords")
    tone_id = fields.Many2one(comodel_name='openai.prompt.tone', domain =_get_tone_domain, default=lambda self: self._default_tone())
    
    
    @api.onchange('tone_id')
    def _onchange_tone(self):
        if self.tone_id:
            self.tone_id  = self.tone_id

    
    
    def open_suggest_seo_wizard(self):
        ctx = {
                'active_model_id' : self.env.context.get('active_model_id'), 
                'active_model_name' : self.env.context.get('active_model_name'),
                'active_field' : self.env.context.get('active_field'),  
                'active_content' : self.env.context.get('active_content'),  
            }
        wizard_id = self.env.ref('wk_chatgpt_engine.suggest_seo_wizard_form').id
        return {
            'name': 'Suggest SEO correction',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(wizard_id, 'form')],
            'res_model': 'suggest.seo.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }
        
        
    def process_ai_content(self):
        if not self.prompt:
            raise UserError("Please fill the Content")
        prompt  = self.prompt
        suggest_seo = self.find_suggest_seo()
        temperature = suggest_seo.temperature
        ai_model = suggest_seo.openai_model
        odoo_api_key = self.env['ir.config_parameter'].sudo().get_param('wk_chatgpt_engine.api_key_action')
        if odoo_api_key == 'openai_api_key':
            configuration = self.env['open.ai.configuration'].search([], limit=1)
            response = configuration.suggest_seo_content(prompt, temperature, ai_model)
        else:
            conversation_history = [{'role': 'system', 'content': 'You are a helpful assistant with the aim of professionally generating content for the user.'}, {'role': 'assistant', 'content': 'What do you need ?'}, {'role': 'user', 'content': f'{prompt}'}]
            response = Web_Editor.generate_text(self,prompt, conversation_history)
        self.ensure_one()
        return response
    
            
    def _get_meta_data(self, lines):
        meta_data = {}
        for line in lines:
            key_value = line.split(':', 1)  
            if len(key_value) == 2:
                key = key_value[0].strip().lower()
                value = key_value[1].strip()
                meta_data[key] = value  
        
        return meta_data  
       
    
    def preview_suggest_seo_content(self):
        response = self.process_ai_content()
        odoo_api_key = self.env['ir.config_parameter'].sudo().get_param('wk_chatgpt_engine.api_key_action')
        if odoo_api_key == 'openai_api_key':
            if not response['status']:
                raise UserError(response['message'])
            lines = response['content'].split('\n')
        else:
            lines = response.split('\n')
            
        meta_data = self._get_meta_data(lines)
        meta_title = meta_data.get('meta title', '')
        meta_description = meta_data.get('meta description', '')
        meta_keywords = meta_data.get('meta keywords', '')
        self.write({
            'meta_title' :  meta_title,
            'meta_description' :  meta_description,
            'meta_keywords'  : meta_keywords
        })
        return {
            'name': 'Preview Content',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'suggest.seo.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
  
    
    def save_suggest_seo_content(self):
        product_id = self.env.context.get("product")
        active_model = self.env.context.get("model_active")
        product = self.env[active_model].browse(product_id)
        odoo_api_key = self.env['ir.config_parameter'].sudo().get_param('wk_chatgpt_engine.api_key_action')
        
        if self.meta_description or self.meta_keywords:
            product.write({
                'website_meta_title' :  self.meta_title,
                'website_meta_description' :  self.meta_description,
                'website_meta_keywords'  : self.meta_keywords
            })

        else:
            response = self.process_ai_content()
            if odoo_api_key == 'openai_api_key':
                if not response.get('status'):
                    raise UserError(response.get('message'))
                lines = response['content'].split('\n')
            else:
                lines = response.split('\n')
            meta_data = self._get_meta_data(lines)
            meta_title = meta_data.get('meta title', '')
            meta_description = meta_data.get('meta description', '')
            meta_keywords = meta_data.get('meta keywords', '')
            product.write({
                'website_meta_title' :  meta_title,
                'website_meta_description' :  meta_description,
                'website_meta_keywords'  : meta_keywords
            })




    #   BULK SEO Update 
    def _get_seo_prompt(self, model, suggest_seo):

        suffixes  = ""
        for field in suggest_seo.model_field_ids:
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
        result = f'Suggest me to create a Meta Title, Meta Description and Meta Keywords in a Professional manner:\n{suffixes}'
        return result

            


    def action_bulk_seo_update(self):
        products = self.env.context.get("active_ids")
        model = self.env.context.get("active_model")
        ProductModel = self.env[model]
        configuration = self.env['open.ai.configuration'].search([], limit=1)
        suggest_seo = self.env['openai.suggest.seo'].search([('model_id', '=', self.env.context.get('active_model'))], limit=1)
        bulk_records_config = self.env['ir.config_parameter'].sudo().get_param('wk_chatgpt_engine.max_bulk_records')

        if len(products) > int(bulk_records_config):
            raise UserError(f"You can't Select more than {bulk_records_config} records")
        for product_id in products:
            product = ProductModel.sudo().browse(product_id)
            prompt = self._get_seo_prompt(product, suggest_seo)
            try:
                response = configuration.seo_bulk_update(prompt)
            except Exception as e:
                raise UserError(f"Error updating SEO for product {product.name}: {e}")
            
            if not response.get('status'):
                raise UserError(response.get('message'))
            
            lines = response['content'].split('\n')
            meta_data = self._get_meta_data(lines)
            meta_title = meta_data.get('meta title', '')
            meta_description = meta_data.get('meta description', '')
            meta_keywords = meta_data.get('meta keywords', '')
            product.sudo().write({
                'website_meta_title': meta_title,
                'website_meta_description': meta_description,
                'website_meta_keywords': meta_keywords,
            })
