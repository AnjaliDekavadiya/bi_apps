# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Material Requisition',
        readonly=True,
    )
