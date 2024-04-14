# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, fields, models, _


class AiBotCommonFields(models.Model):

    _name = 'ai.common.fields.line'
    _description = "Ai Common Fields.Line"
    _order = "sequence"

    name = fields.Char("Label", required=True)
    value = fields.Text("Value", required=True)
    config_id = fields.Many2one("ai.bot.config")
    sequence = fields.Integer("Sequence")
