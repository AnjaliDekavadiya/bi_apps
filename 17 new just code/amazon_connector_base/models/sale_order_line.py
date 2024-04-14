from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if (not self.order_id.amz_marketplace_id.account_id):
            return res
        #res['account_id'] = self.order_id.amz_marketplace_id.account_id.id

        return res
