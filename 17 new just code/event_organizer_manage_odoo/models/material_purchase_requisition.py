# -*- coding: utf-8 -*-

from odoo import models, fields

class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition' 
    
    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False,
    )

