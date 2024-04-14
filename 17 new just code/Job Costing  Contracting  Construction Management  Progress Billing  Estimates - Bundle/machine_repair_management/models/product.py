# -*- coding: utf-8 -*

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    brand = fields.Char(
        string = "Brand"
    )
    color_custom = fields.Char(
        string = "Color"
    )
    model = fields.Char(
        string="Model"
    )
    year = fields.Integer(
        string="Year"
    )
    is_machine = fields.Boolean(
        string="Is Machine"
    )
    machine_repair_ids = fields.One2many(
        'machine.repair.support',
        'product_id',
        string='Machine Repair Request',
        copy=False,
        readonly=True,
    )
    
    
#    @api.multi odoo13
    def action_machine_repair_request(self):
        self.ensure_one()
        # res = self.env.ref('machine_repair_management.action_machine_repair_support')
        # res = res.sudo().read()[0]
        res = self.env["ir.actions.actions"]._for_xml_id("machine_repair_management.action_machine_repair_support")
        res['domain'] = str([('product_id', '=', self.id)])
        return res
