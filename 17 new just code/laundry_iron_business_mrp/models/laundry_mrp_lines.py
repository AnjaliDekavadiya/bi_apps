# -*- coding: utf-8 -*

from odoo import models, fields, api

class LaundryMrpLine(models.Model):
    _name = 'laundry.mrp.line'
    _description = 'Laundry Manufacturing Lines'
    

    custom_product_id = fields.Many2one(
        'product.product',
        required=True,
        string='Product',
        copy=True,
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        'Product Template', 
        related='custom_product_id.product_tmpl_id',
        store=True, 
        readonly=False
    )
    custom_quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=False,
        copy=True,
    )
    custom_uom_id = fields.Many2one(
        'uom.uom',
        string='UOM',
        required=False,
        copy=True,
    )
    custom_bom_id = fields.Many2one(
        'mrp.bom',
        string='BOM',
        copy=True,
        required=False
    )
    laundry_service_request_id = fields.Many2one(
        'laundry.business.service.custom',
        string='Laundry Request',
        copy=False,
        readonly=True,
    )
    mrp_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        copy=False,
    )

    @api.onchange('custom_product_id')
    def custom_set_uom(self):
        self.custom_uom_id = self.custom_product_id.uom_id

    def create_mrp_custom(self):
        self.ensure_one()
        action = self.env.ref('mrp.mrp_production_action').sudo().read()[0]
        action['views'] = [(self.env.ref('mrp.mrp_production_form_view').id, 'form')]
        action['context'] = {
            'default_product_id': self.custom_product_id.id,
            'default_product_qty': self.custom_quantity,
            'default_product_uom_id': self.custom_uom_id.id,
            'default_date_planned_start': fields.Datetime.now(),
            'default_company_id': self.laundry_service_request_id.company_id.id,
            'default_bom_id': self.custom_bom_id.id,
            'default_custom_laundry_request_id': self.laundry_service_request_id.id,
            'default_custom_mrpline_id' : self.id
        }
        return action
       

            