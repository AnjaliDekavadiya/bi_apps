from odoo import models, fields, api


class productInherit(models.Model):
    _inherit = 'product.template'
    _description = 'product.template'

    cloth_type = fields.Many2one('tailoring.cloth_type','Cloth type')
    description = fields.Text('Description')
    fabric = fields.Char(string="Fabric type",related='cloth_type.fabric_id.name')
    detailed_type = fields.Selection([('consu','Consumable'),('service','Service'),('product','Storable Product')],string='Product Type',default='product')
