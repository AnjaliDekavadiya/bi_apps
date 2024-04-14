# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###############################################################################


from odoo import api, models, fields
from odoo.exceptions import UserError
import logging
import re

_logger = logging.getLogger(__name__)



class AiBulkContentWizard(models.TransientModel):
    _name = "ai.bulk.content.wizard"
    _description = "AI Bulk Content Wizard"


    def find_prompt_instruction(self):
        prompt_instruct = self.env['openai.prompt.instruction'].search([('model_id', '=', self.env.context.get('active_model') )], limit=1)
        return prompt_instruct

    def _get_maximum_tokens(self):
        prompt_instruct = self.find_prompt_instruction()
        return prompt_instruct.content_length if prompt_instruct else 250
    
    def _get_default_model(self):
        model = self.env["ir.model"].search([("model","=",self.env.context.get('active_model'))])
        return model.id
    

    
    def _get_tone_domain(self):
        active_model = self.env.context.get('active_model')
        if active_model:
            prompt_instruct = self.find_prompt_instruction()

            if prompt_instruct:
                return [('id', 'in', prompt_instruct.tone_ids.ids)]
        
        return [('visibility', '=', 'global')]

    max_token = fields.Integer(string="Maximum Content length", default=_get_maximum_tokens, help="Choose the length of the AI Content.")
    model_id = fields.Many2one(comodel_name="ir.model", string="Models", default=_get_default_model)
    model_field_id = fields.Many2one(comodel_name='ir.model.fields',domain="[('model_id','=', model_id ), ('ttype','in', ['text', 'html'])]" , string="Model Fields", required=True)
    tone_id = fields.Many2one(comodel_name='openai.prompt.tone', domain =_get_tone_domain, string="Choose Tone")




    def action_generate_bulk_content(self):
        ctx = {'product_ids': self.env.context.get("active_ids")}
        wizard_id = self.env.ref('wk_chatgpt_engine.generate_bulk_content_form').id
        return {
            'name': ('Generate Bulk Record'),
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(wizard_id, 'form')],
            'res_model': 'ai.bulk.content.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }
    

    def get_product_summary(self):
        product_ids = self.env.context.get("product_ids")
        active_model = self.env.context.get("active_model")
        model_ids = self.env[active_model].browse(product_ids)
        prompt_instruct = self.find_prompt_instruction()
        tone = f'{self.tone_id.content_style} using the following product details to summarize your description:\n'
        output = []

        if model_ids and self.tone_id and prompt_instruct.model_field_ids:
            for model in model_ids:
                model_summary = {}
                for field in prompt_instruct.model_field_ids:
                    field_summary = self.get_field_summary(model, field)
                    if field_summary:
                        model_summary[field.field_description] = field_summary
                
                if model_summary:
                    output.append(f"{f'product_id={model.id}'}:\n{model_summary},\n")

            return ''.join(output)


    def get_field_summary(self, model, field):
        if field.ttype == 'many2one':
            value = model[field.name].name
            if value:
                return f'{value}\n'
        elif field.ttype == 'one2many':
            if field.name == 'attribute_line_ids':
                values = model[field.name]
                attributes_summary = []
                for value in values:
                    key = value.attribute_id.name
                    pair = ", ".join(v.name for v in value.value_ids)
                    attributes_summary.append(f"{key}: {pair}\n")
                return '\n'.join(attributes_summary)
            elif field.name == 'product_template_variant_value_ids':
                # Handle this case as needed
                pass
        elif field.ttype == 'many2many':
            values = model[field.name].mapped("name")
            value = ", ".join(values)
            if value:
                return f'{value}\n'
        elif field.ttype in ['char', 'text', 'html', 'integer', 'float'] and field.name in model:
            value = model[field.name]
            if value:
                return f'{value}\n'

        return None
               

    def process_bulk_ai_content(self):
        product_ids = self.env.context.get("product_ids")
        active_model = self.env.context.get("active_model")
        model_ids = self.env[active_model].browse(product_ids)
        prompt_instruct = self.find_prompt_instruction()
        temperature = prompt_instruct.temperature
        ai_model = prompt_instruct.openai_model
        bulk = self._bulk_product_name(model_ids)
        




    def split_products(self, products):
        split_lists = [products[i:i+20] for i in range(0, len(products), 20)]
        return split_lists

    def _bulk_product_name(self, product_ids):
        products = [f'{product.id} :[name :{product.name}\n category name : {product.categ_id.name}\n' for product in product_ids if product_ids]
        result= {}
        split_lists = self.split_products(products)
        final_lst = [lst for lst in split_lists]
        return final_lst


                    


