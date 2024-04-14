from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    amz_transaction_inv_id = fields.Char("Amazon Transaction Invoice ID")
    amz_shipment_id = fields.Char("Amazon Shipment ID")
    amz_shipment_date = fields.Datetime("Amazon Shipment Date")
    amz_transaction_refund_id = fields.Char("Amazon Transaction Refund ID")
    item_promotion_id = fields.Char("Item Promotion ID")
    ship_promotion_id = fields.Char("Ship Promotion ID")
    ship_from_address = fields.Char("Ship From Address")
    fulfillment_center_id = fields.Many2one("amazon.fulfillment.center", "Fulfillment Center")
    ship_from_country_id = fields.Many2one("res.country", "Ship From Country")
    amz_total_net_line_amount = fields.Float("Total Amazon Net Amount of SO line")
    amz_total_tax_line_amount = fields.Float("Total Amazon Tax Amount of SO line")
    quantity_returned = fields.Float(
        "Returned Quantity", compute="_compute_returned_quantity")
    amazon_product_id = fields.Many2one("amazon.offer", string="Amazon Product")

    @api.depends(
        'move_ids.returned_move_ids.state',
        'move_ids.returned_move_ids.product_uom_qty',
        'move_ids.product_uom'
    )
    def _compute_returned_quantity(self):
        for line in self:  # TODO: maybe one day, this should be done in SQL for performance sake
            if line.qty_delivered_method == 'stock_move':
                qty = 0.0
                for move in line.move_ids.mapped("returned_move_ids"):
                    if move.state != 'done':
                        continue
                    qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                line.quantity_returned = qty
