# -*- coding: utf-8 -*-

from odoo import models, fields , api


class MaterialRequisitionFleetLine(models.Model):
    _name = "material.requisition.fleet.req"
    _description = 'Material Requisition Fleet Request'

    fleet_request_id = fields.Many2one(
        'fleet.request',
        string='Fleet Request',
        copy=False,
    )
    requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=False,
    )
    requisition_type = fields.Selection(
        selection=[
        ('internal','Internal Picking'),
        ('purchase','Purchase Order')],
        string='Requisition Action',
        default='purchase',
        required=True,
        copy=False,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        copy=False,
    )
    qty = fields.Float(
        string='Quantity',
        default=1,
        required=True,
        copy=False,
    )
    uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
        copy=False,
    )
    description = fields.Char(
        string='Description',
        required=True,
        copy=False,
    )
    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        related='requisition_line_id.requisition_id',
        string='Requisition',
        copy=False,
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
