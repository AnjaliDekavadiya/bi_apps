# -*- coding: utf-8 -*-

from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    # inventory_tag_ids = fields.Many2many(
    #     'inventory.tags',
    #     string='Inventory Tags',
    #     readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    # )
    inventory_tag_ids = fields.Many2many(
        'inventory.tags',
        string = 'Inventory Tags',
        readonly=True
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
