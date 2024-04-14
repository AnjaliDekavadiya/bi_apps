# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime


class helpdeskAssetsEequipmentLine(models.Model):

    _name = 'helpdesk.assets.equipment.line'
    _description = "Helpdesk Assets Equipment Line"
    
    maintenance_equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Equipment',
        required=True,
    )

    helpdesk_assets_equipment_id= fields.Many2one(
        'helpdesk.assets.equipment',
        string='helpdesk assets equipment'
    )


    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )

    description = fields.Char(
        'Description',
        required=True,

    )

    start_date = fields.Datetime(
        'Start Date',
        required=True,
    )

    end_date = fields.Datetime(
        'End Date',
        required=True,
    )

    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )

    product_uom_qty = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
    )
    
    @api.onchange('maintenance_equipment_id')
    def _onchange_maintenance_equipment_id(self):
        for rec in self:
            rec.description = rec.maintenance_equipment_id.name

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_uom = rec.product_id.uom_id
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
        
