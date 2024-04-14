# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
#See LICENSE file for full copyright and licensing details.

from odoo import models, fields , api

class MaterialRequisitionCarRepair(models.Model):
    _name = "material.requisition.car.repair"
    _description = 'material.requisition.car.repair'

    requisition_id = fields.Many2one(
        'car.repair.support',
        string='Requisitions',
    )
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisition Line',
        copy=False,
        readonly=True
    )
    custom_material_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Material Requisition',
        related ='custom_requisition_line_id.requisition_id',
        copy=False,
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    qty = fields.Float(
        string='Quantity',
        default=1,
        required=True,
    )
    uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    requisition_type = fields.Selection(
        selection=[
                    ('internal','Internal Picking'),
                    ('purchase','Purchase Order'),
        ],
        string='Requisition Action',
        default='purchase',
        required=True,
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
