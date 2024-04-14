# -*- coding: utf-8 -*-

from odoo import models, fields


class HelpdeskLevelConfig(models.Model):
    _name = 'helpdesk.level.config'
    _description = 'Helpdesk Level Configuration'

    name = fields.Char(
        string="Name",
        required=True,
    )
    line_ids = fields.One2many(
        'helpdesk.level.config.line',
        'level_config_id',
        string="Level Configurations",
    )

class HelpdeskLevelConfigLines(models.Model):
    _name = 'helpdesk.level.config.line'
    _description = 'Helpdesk Level Configuration Line'

    level_config_id = fields.Many2one(
        'helpdesk.level.config',
        string="Level Config",
    )
    category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('support', 'Support')],
        string='Category',
        required=True,
    )
    priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
#        [('0', 'Normal'),
 #       ('1', 'Low'),
  #      ('2', 'High'),
   #     ('3', 'Very High')],
        string='Priority',
        required=True,
    )
    period_number = fields.Integer(
        string="Gap",
        required=True,
    )
    period_type = fields.Selection(
        [('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks')],
        string="Period Type",
        required=True,
    )
