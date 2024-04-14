# -*- coding: utf-8 -*-

from odoo import models, fields , api


class MaterialRequisitionClothLine(models.Model):
    _name = "material.requisition.cloth.req"
    _description = 'Material Requisition Cloth Request'

    cloth_request_id = fields.Many2one(
        'cloth.request.details',
        string='Cloth Request',
    )
    workorder_request_id = fields.Many2one(
        'project.task',
        string='Workorder Request',
    )
    requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
    )
    requisition_type = fields.Selection(
        selection=[
        ('internal','Internal Picking'),
        ('purchase','Purchase Order')],
        string='Requisition Action',
        default='internal',
        required=True,
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
    requisition_id = fields.Many2one(
        'material.purchase.requisition',
        related='requisition_line_id.requisition_id',
        string='Requisition',
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
