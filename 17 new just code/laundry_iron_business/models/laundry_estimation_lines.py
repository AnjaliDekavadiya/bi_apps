# -*- coding: utf-8 -*

from odoo import models, fields, api

class LaundryQuotLine(models.Model):
    _name = 'laundry.line.quot'
    _description = 'Laundry Line Quotation'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    description = fields.Char(
        string='Description',
    )
    qty = fields.Float(
        string='Quantity',
        default=1,
    )
    price = fields.Float(
        string='Price',
    )
    total = fields.Float(
        string='Total',
        compute='_compute_total_price',
        store=True
    )
    laundry_id = fields.Many2one(
        'laundry.business.service.custom',
        string='Laundry',
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string="UOM"
    )

    @api.depends('price','qty')
    def _compute_total_price(self):
        for rec in self:
            rec.total = rec.price * rec.qty

    @api.onchange('product_id')
    def onchange_product(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.price = rec.product_id.lst_price
            rec.product_uom = rec.product_id.uom_id.id


class LaundryServiceEstimationLines(models.Model):
    _name = 'laundry.service.estimation.lines'
    _description ="Laundry Service Estimation Lines"
    
    task_id = fields.Many2one(
        'project.task',
        string="Task"
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )
    qty = fields.Float(
        string = "Quantity",
        default=1.0
    )
    product_uom = fields.Many2one(
        'uom.uom',
        string="UOM"
    )
    price = fields.Float(
        string = "Price"
    )
    notes = fields.Text(
       string="Notes",
    )
    
    @api.onchange('product_id')
    def product_id_change(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id.id
            rec.price = rec.product_id.lst_price
