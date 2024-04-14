# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string="Cloth Request"
    )