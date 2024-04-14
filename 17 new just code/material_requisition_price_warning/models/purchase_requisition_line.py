# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaterialPurchaseRequisitionLine(models.Model):
    _inherit = "material.purchase.requisition.line"

    custom_currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        related='requisition_id.custom_currency_id',
        store=True,
        readonly=True,
        copy = False
    )
    cost_price = fields.Float(
        compute='_compute_total_cost_price', 
        string='Cost Price',
        required=True,
    )
    total_cost_price = fields.Float(
        compute='_compute_total_cost_price',
        string='Subtotal',
        readonly=True
    )

    # @api.one #odoo13
    # @api.depends('product_id', 'qty', 'cost_price')
    # def _compute_total_cost_price(self):
    #     self.cost_price = self.product_id.standard_price
    #     self.total_cost_price = self.qty * self.cost_price

    @api.depends('product_id', 'qty', 'cost_price')
    def _compute_total_cost_price(self):
        for rec in self:
            rec.cost_price = rec.product_id.standard_price
            rec.total_cost_price = rec.qty * rec.cost_price

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
