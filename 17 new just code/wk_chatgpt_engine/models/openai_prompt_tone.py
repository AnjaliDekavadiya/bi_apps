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


VISIBILE = [
    ('global', 'Global'),
    ('specific', 'Specific Model'),
]



class OpenAiPromptTone(models.Model):
    _name = "openai.prompt.tone"
    _description = 'OPENAI Prompt Tone'
    _order = "sequence"



    name = fields.Char(string="Name", required=True)
    content_style = fields.Char(string="Content Style")
    visibility = fields.Selection(selection=VISIBILE, string="Visibility", default="specific")
    model_id = fields.Many2one("ir.model", string="Instruct Model", related="instuction_id.model_id", readonly=False)
    instuction_id = fields.Many2one(comodel_name="openai.prompt.instruction", string="Instructions")
    tone_id = fields.Many2one(comodel_name="openai.suggest.seo", string="SEO Tone")
    tone_model_id = fields.Many2one("ir.model", string="Seo Model", related="tone_id.model_id", readonly=False)
    sequence = fields.Integer(default=1)



    @api.onchange('name', 'tone_id', 'instuction_id')
    def _onchange_content_style(self):
        if self.name:
            if self.tone_id:
                self.content_style = f'Suggest me to create a Meta Title, Meta Description and Meta Keywords in a {self.name.capitalize()} manner'
            elif self.instuction_id:
                self.content_style = f'Write a Product Description in a {self.name.capitalize()} manner'
            else:
                self.content_style = False




