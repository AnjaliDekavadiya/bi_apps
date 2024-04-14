from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    no_of_labels = fields.Char(string="No Of Labels",default=1,copy=False)
    parcel_ids = fields.Char("parcel ID",copy=False)
