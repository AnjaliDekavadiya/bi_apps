from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        related="sale_line_id.order_id",
        store=True, readonly=True
    )
    ship_from_country_id = fields.Many2one(
        comodel_name="res.country",
        related="sale_line_id.ship_from_country_id",
        store=True, readonly=True
    )
    fba_stock_report_id = fields.Many2one(
        comodel_name="amazon.report.log",
        string="FBA Stock Report",
    )
