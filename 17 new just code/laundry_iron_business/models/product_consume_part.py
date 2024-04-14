# -*- coding: utf-8 -*

from odoo import models, fields, api

class LaundryProductConsumePart(models.Model):
    _name = 'laundry.product.consume.part'
    _description = "Laundry Product Consume Part"
    
    laundry_id = fields.Many2one(
        'project.task',
        string="Laundry Business Service",
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string = "Product",
        required=True,
    )
    qty = fields.Float(
        string = "Quantity",
        default=1.0,
        required=True,
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string="UOM",
        required=True,
    )

    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id.id
