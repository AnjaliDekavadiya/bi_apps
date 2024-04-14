# Copyright 2019-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_method_id = fields.Many2one(
        "account.journal",
        domain=[("type", "in", ["bank", "cash"])],
        string="Payment Method",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id_warning(self):
        res = super()._onchange_partner_id_warning()
        if self.partner_id.commercial_partner_id.sale_payment_method_id:
            self.payment_method_id = (
                self.partner_id.commercial_partner_id.sale_payment_method_id.id
            )
        elif self.partner_id.sale_payment_method_id:
            self.payment_method_id = self.partner_id.sale_payment_method_id.id
        return res
