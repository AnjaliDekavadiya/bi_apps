# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class CarCostLine(models.Model):
    _name = "car.jobcost.line"
    _description = "Car JobCost Line"

    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.product_qty = 1.0
            rec.uom_id = rec.product_id.uom_id.id
            rec.cost_price = rec.product_id.standard_price
    
    @api.depends('product_qty','hours','cost_price')
    def _compute_total_cost(self):
        for rec in self:
            if rec.job_type == 'labour':
                rec.product_qty = 0.0
                rec.total_cost = rec.hours * rec.cost_price
            else:
                rec.hours = 0.0
                rec.total_cost = rec.product_qty * rec.cost_price
    
    date = fields.Date(
        string="Date",
    )
    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')
                ],
        string="Type",
        required=True
    )
    job_type_id = fields.Many2one(
        'job.type',
        string="Job Type"
    )
    product_id = fields.Many2one(
        'product.product',
        string="Product",
        required=True
    )
    description = fields.Char(
        string="Description"
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
    )
    product_qty = fields.Float(
        string="Quantity",
    )
    car_support_id = fields.Many2one(
        'car.repair.support',
        string="Car Support",
    )
    cost_price = fields.Float(
        string="Cost"
    )
    total_cost = fields.Float(
        string="Total Cost",
        compute='_compute_total_cost',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env.user.company_id.currency_id, 
        readonly=True
    )
    hours = fields.Float(
        string='Hours'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
