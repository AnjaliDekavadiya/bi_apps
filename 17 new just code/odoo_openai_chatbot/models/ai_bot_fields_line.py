# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _




class AiBotConfigFields(models.Model):

    _name = 'ai.bot.fields.line'
    _description = "Ai Bot Fields.Line"
    _order = "sequence"

    name = fields.Char("Label", required=True)
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Fields",
        help="Fields that used in the content generation.",
        required=True,
        ondelete='cascade'
    )
    
    config_id = fields.Many2one("ai.bot.config")
    sequence = fields.Integer("Sequence")
    
    @api.onchange('field_id')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    def _add_default_label(self):
        if self.field_id:
            self.name = self.field_id.field_description
        else:
            self.name = ''
    
    
    
   