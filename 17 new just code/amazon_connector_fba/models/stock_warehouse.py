from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    is_fba_wh = fields.Boolean(
        string="Is Amazon FBA Warehouse?",
    )
