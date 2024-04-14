# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class ClothRequestStage(models.Model):
    _inherit = 'cloth.request.stage'

    probc_is_repair_stage = fields.Boolean(
        string="Is Repair Stage"
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: