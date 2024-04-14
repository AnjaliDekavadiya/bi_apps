# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ManufacturingProduction(models.TransientModel):
    _name = "manufacturing.production.wiz"
    _description = 'Manufacturing Production Wizard'

    production_line_ids = fields.One2many(
        'manufacturing.production.line.wiz',
        'production_wiz_id',
        string='Production Lines'
    )


    @api.model
    def default_get(self, fields):
        res = super(ManufacturingProduction, self).default_get(fields)
        active_id = self._context.get('active_ids')
        purchase_req_id = self.env[self._context['active_model']].browse(active_id)
        production_lst = []
        for line in purchase_req_id.requisition_line_ids:
            if line.requisition_type == 'manufacturing':
                production_lst.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_tmpl_id': line.product_id.product_tmpl_id.id,
                    'requisition_line_id': line.id}))
        if production_lst:
            res.update({
                'production_line_ids': production_lst,
            })
        return res

    #@api.multi
    def create_production(self):
        for rec in self:
            for line in rec.production_line_ids:
                mrp_vals = {
                    'product_id': line.requisition_line_id.product_id.id,
                    'product_qty': line.requisition_line_id.qty,
                    'product_uom_id': line.requisition_line_id.uom.id,
                    # 'date_planned_start': fields.Datetime.now(),
                    'date_start': fields.Datetime.now(),
                    'company_id': line.requisition_line_id.requisition_id.company_id.id,
                    'bom_id': line.bom_id.id,
                    'requisition_id': line.requisition_line_id.requisition_id.id,
                }
                mrp_production_id = self.env['mrp.production'].create(mrp_vals)
                # mrp_production_id._onchange_move_raw()
                # mrp_production_id.onchange_product_id()
                mrp_production_id._onchange_product_id()
                if mrp_production_id:
                    line.requisition_line_id.requisition_id.write({
                        'is_production_created': True,
                    })

class ManufacturingProductionLine(models.TransientModel):
    _name = "manufacturing.production.line.wiz"
    _description = 'Manufacturing Production Line Wizard'
    
    production_wiz_id = fields.Many2one(
        'manufacturing.production.wiz',
        string="Production",
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        # readonly=True,
        store=True,
    )
    requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string="Requisition Line",
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        # readonly=True,
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        string="Bill of Material",
        required=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
