# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###############################################################################

from odoo import api, models, fields
from odoo.exceptions import ValidationError 



MODEL = [
    ('product', 'Product'),
    ('category', 'Public Category'),
]


class OpenAiSuggestSeo(models.Model):
    _name = "openai.suggest.seo"
    _description = 'OPENAI Suggest SEO'
    
    
    def _get_model_list(self):
        allowed_model_ids = ['gpt-4', 'gpt-4-0613', 'gpt-4-vision-preview', 'gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'gpt-3.5-turbo-16k-0613', 'gpt-3.5-turbo-16k', 'gpt-4-1106-preview']
        
        configuration = self.env['open.ai.configuration'].search([], limit=1)
        response = configuration.get_model_lists()
        
        data_list = response.get('data', [])
        
        model_lists = [
            (item['id'], item['id'].replace('-', ' ').upper())
            for item in data_list
            if item['id'] in allowed_model_ids
        ]
        
        if model_lists:
            return model_lists
        else:
            return [('gpt-3.5-turbo', 'gpt-3.5-turbo')]
    
    
    name = fields.Char("Name", required=True)   
    meta_title = fields.Char("Meta Title")
    meta_description = fields.Char("Meta Description")
    meta_keyword =  fields.Char("Meta Keywords")

    temperature = fields.Float(string="Temperature", default=1, help='What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.')
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='SEO Meta Configuration for',
        ondelete='cascade',
        required=True,
        help='Select Model for SEO configuration',
        domain="[('model', 'in', ['product.template', 'product.public.category'])]"
    )
    model_field_ids = fields.Many2many(
    comodel_name='ir.model.fields', domain="[('model_id','=', model_id ),('ttype','in', ['char','text','html', 'integer', 'float', 'many2one', 'many2many', 'one2many'])]", string="Model Fields", help="Fields utilized in Meta Title, Meta Description, and Meta Keywords.")
    tone_ids = fields.One2many('openai.prompt.tone', 'tone_id', string='Tones')
    openai_model = fields.Selection(selection="_get_model_list", default="gpt-3.5-turbo", string="OpenAi Model", required=True)
    bulk_action_id = fields.Many2one(comodel_name='ir.actions.server')
    bulk_update = fields.Boolean(string="Bulk Allow")



    _sql_constraints = [('unique_name', 'unique(model_id)', 'A single SEO can be configured for a model!')]



    def action_allow_bulk_updates(self):
        action = False
        if self.bulk_action_id:
            self.bulk_action_id.create_action()
            self.bulk_update = True
        else:
            action = self.env["ir.actions.server"].create({
                "name": "Generate Bulk SEO",
                "model_id": self.model_id.id,
                "type": "ir.actions.server",
                "state": 'code',
                "code" :  """action = env['suggest.seo.wizard'].action_bulk_seo_update()""",
            })
            self.bulk_action_id =  action.id
            action.create_action()
            self.bulk_update = True
        return action


    

    def action_disallow_bulk_updates(self):
        self.bulk_action_id.unlink_action()
        self.bulk_update = False