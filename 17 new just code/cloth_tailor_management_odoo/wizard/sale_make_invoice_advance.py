# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"


    # def _prepare_invoice_values(self, order, name, amount, so_line):
    def _prepare_invoice_values(self, order, so_line):
        res = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, so_line)
        if order and order.custom_cloth_request_ids:
            res.update({
                'custom_cloth_request_ids': [(6, 0, order.custom_cloth_request_ids.ids)]
            })
        return res