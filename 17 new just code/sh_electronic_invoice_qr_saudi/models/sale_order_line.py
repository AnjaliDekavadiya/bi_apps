from odoo import api,models, fields

class saudi_sale_orderline(models.Model):
    _inherit = 'sale.order.line'

    taxable_amount = fields.Float("Taxable Amount",compute="get_computable_tax")

    @api.depends('price_unit','product_uom_qty')
    def get_computable_tax(self):
        for rec in self:
            rec.taxable_amount = 0.0
            if rec.price_unit and rec.product_uom_qty:
                rec.taxable_amount = rec.price_unit * rec.product_uom_qty
