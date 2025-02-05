# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    #@api.multi
    @api.depends('origin', 'sale_id', 'purchase_id', 'state')
    def _compute_inventory_tags(self):
        for rec in self:
            if rec.sale_id:
                rec.inventory_tag_ids = rec.sale_id.inventory_tag_ids.ids
            if rec.purchase_id:
                rec.inventory_tag_ids = rec.purchase_id.inventory_tag_ids.ids


    inventory_tag_ids = fields.Many2many(
        'inventory.tags',
        string='Inventory Tags',
        compute='_compute_inventory_tags',
        store=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
