from odoo import fields, models, _
from odoo.exceptions import UserError


class AmazonOperationWizard(models.TransientModel):
    _inherit = "amazon.operation.wizard"

    orders_list = fields.Char("Orders List", help="Enter comma separated Amazon Order Refs.")


    def execute_amazon_operations(self):
        if self.is_import_order and self.orders_list:
            orders = self.env["sale.order"].import_amazon_order(
                self.amz_account_id, self.orders_list)
            return {
                'name': _('Imported Amazon Orders'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': [('id', 'in', orders.ids)],
            }
        return super().execute_amazon_operations()
