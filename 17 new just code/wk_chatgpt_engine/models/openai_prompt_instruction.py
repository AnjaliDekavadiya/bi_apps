# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###############################################################################


from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)


class OpenAiPromptInstruction(models.Model):
    _name = "openai.prompt.instruction"
    _description = 'OPENAI Prompt Instruction'




    name = fields.Char(string="Name", required=True)
    temperature = fields.Float(string="Temperature", default=1, help='This value decides the creativity and diversity of the text.')
    content_length = fields.Integer(string="Content Length", default=200, help='This value decides the maximum length of AI content response')
    model_id = fields.Many2one(comodel_name="ir.model", string="Models", ondelete='cascade', required=True, help='Select Model for Prompt Instruction')
    model_field_ids = fields.Many2many(
    comodel_name='ir.model.fields', domain="[('model_id','=', model_id ),('ttype','in', ['char','text','html', 'integer', 'float', 'many2one', 'many2many', 'one2many'])]", string="Model Fields")
    tone_ids = fields.One2many('openai.prompt.tone', 'instuction_id', string='Tone')
    openai_model = fields.Selection(
        selection="_get_model_list", default="gpt-3.5-turbo", string="OpenAi Model", required=True)
    bulk_action_id = fields.Many2one(comodel_name='ir.actions.server')
    bulk_update = fields.Boolean(string="Bulk Done")
    
    
    _sql_constraints = [('unique_name', 'unique(model_id)', 'A single Instruction can be configured for a model!')]


    _sql_constraints = [
        ('check_temperature_range', 'CHECK (temperature >= 0 AND temperature <= 2)',
         'The value of Temperature must be between 0 and 2.')
    ]

   
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


    def action_allow_bulk_updates(self):
        action = False
        if self.bulk_action_id:
            self.bulk_action_id.create_action()
            self.bulk_update = True
        else:
            action = self.env["ir.actions.server"].create({
                "name": "Generate Bulk Content",
                "model_id": self.model_id.id,
                "type": "ir.actions.server",
                "state": 'code',
                "code" :  """action = env['ai.bulk.content.wizard'].action_generate_bulk_content()""",
            })
            self.bulk_action_id =  action.id
            action.create_action()
            self.bulk_update = True
        return action


    def action_disallow_bulk_updates(self):
        self.bulk_action_id.unlink_action()
        self.bulk_update = False



    

    


