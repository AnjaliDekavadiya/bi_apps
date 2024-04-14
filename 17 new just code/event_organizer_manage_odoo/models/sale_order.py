# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    )

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({
            'event_custom_id': self.event_custom_id.id,
        })
        return result

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        res.event_custom_id = order.event_custom_id
        return res
