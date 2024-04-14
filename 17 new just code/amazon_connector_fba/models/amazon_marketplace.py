
from odoo import api, fields, models


class AmazonMarketplace(models.Model):
    _inherit = 'amazon.marketplace'

    fba_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="FBA Warehouse",
        domain=[("is_fba_wh", "=", True)],
    )
    transit_location_id = fields.Many2one(
        'stock.location',
        string="FBA Transit Location",
        domain=[('usage', '=', 'transit')],
    )
    unsellable_location_id = fields.Many2one(
        'stock.location',
        string="FBA Unsellable Location",
    )

    @api.onchange('fba_warehouse_id')
    def onchange_fba_warehouse_id(self):
        self.fba_location_id = self.fba_warehouse_id.lot_stock_id
