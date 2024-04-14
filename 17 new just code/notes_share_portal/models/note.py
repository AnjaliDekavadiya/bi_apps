# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Task(models.Model):
    _inherit = 'project.task'


    custom_partner_ids = fields.Many2many(
        'res.partner',
        string="Share Portal",
        copy=False
    )