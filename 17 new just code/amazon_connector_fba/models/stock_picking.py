from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    amazon_shipment_id = fields.Char(
        string="Amazon Shipment ID(s)"
    )

    def _check_carrier_details_compliance(self):
        amazon_pickings_sudo = self.sudo().filtered(
            lambda p: p.sale_id
            and p.sale_id.amazon_order_ref
            and p.location_dest_id.usage == 'customer'
        )
        return super(StockPicking, self - amazon_pickings_sudo).\
            _check_carrier_details_compliance()

    def _confirm_shipment(self, account):
        pickings = self.filtered(lambda p: p.carrier_tracking_ref)
        return super(StockPicking, pickings)._confirm_shipment(account)
