
from odoo import fields, models


class AmazonFulfillmentCenter(models.Model):
    _name = 'amazon.fulfillment.center'
    _rec_name = "code"

    fba_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="FBA Stock Warehouse",
        domain=[('is_fba_wh', '=', True)],
    )
    code = fields.Char(name="Fulfillment Center Code", index=True)
    zip_code = fields.Char(name="Fulfillment Center Zip")
    country_id = fields.Many2one("res.country")
