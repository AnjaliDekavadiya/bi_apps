# -*- coding: utf-8 -*-
###############################################################################
#
#  Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
###############################################################################


from odoo import api, models, fields, _
from odoo.exceptions import ValidationError 

import logging
_logger = logging.getLogger(__name__)

MODELS = [
    ('text_davinci_003', 'Text - Davinci'),
    ('text_curie_001', 'Text - Curie'),
    ('text_babbage_001', 'Text - Babbage'),
    ('text_ada_001', 'Text - Ada'),
]



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    api_key_action = fields.Selection(
        selection=[
            ('odoo_api_key', 'Odoo Key (Iap Service)'),
            ('openai_api_key', 'OpenAi API KEY'),
        ],
        default='odoo_api_key', config_parameter='wk_chatgpt_engine.api_key_action')
    api_key = fields.Char(config_parameter='wk_chatgpt_engine.api_key',string="Api Key", default="Dummy", required=True)
    max_bulk_records  =  fields.Integer(config_parameter='wk_chatgpt_engine.max_bulk_records', string="Maximum Bulk Records", help="Set maximum records to update in bulk operation", default=5)
    

            
    @api.constrains('max_bulk_records')
    def _check_positive_values(self):
        for record in self:
            if record.max_bulk_records < 0:
                raise ValidationError(_('Values must be greater than 0'))
            
            

    

 
