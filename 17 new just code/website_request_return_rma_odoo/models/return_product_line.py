# -*- coding: utf-8 -*-

from odoo import models, fields


class ReturnProductLine(models.Model):
    _name = 'return.product.line'
    _description = "Return Product Line"

    return_order_id = fields.Many2one(
        'return.order',
        string='Return Order',
    )
    product_id = fields.Many2one(
        'product.product',
        string="Return Product",
        required=True,
    )
    quantity = fields.Float(
        string='Delivered Quantity',
    )
    return_quantity = fields.Float(
        string='Return Request Quantity',
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Product Uom'
    )
    repair_scrape = fields.Selection([
        ('repair', 'Repairable'),
        ('scrape', 'Scrap'),
        ('ex_change', 'Replacement')],
        string='Repair Method',
#         default='repair',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
