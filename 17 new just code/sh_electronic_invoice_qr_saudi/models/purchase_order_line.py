from odoo import api,models, fields

class saudi_purchase_orderline(models.Model):
    _inherit = 'purchase.order.line'

    taxable_amount = fields.Float("Taxable Amount",compute="get_computable_tax")

    @api.depends('price_unit','product_qty')
    def get_computable_tax(self):
        for rec in self:
            rec.taxable_amount = 0.0
            if rec.price_unit and rec.product_qty:
                rec.taxable_amount = rec.price_unit * rec.product_qty
