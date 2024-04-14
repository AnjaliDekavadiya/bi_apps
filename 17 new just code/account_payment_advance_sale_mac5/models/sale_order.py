from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    advance_payment_ids = fields.One2many('account.payment', 'advance_sale_id',
                                          string="Advanced Payments", readonly=True)
    advance_payment_count = fields.Integer(compute='_compute_advance_payment')
    advance_payment_amount = fields.Monetary(compute='_compute_advance_payment')
    unpaid_amount = fields.Monetary(compute='_compute_advance_payment')

    @api.constrains("partner_invoice_id")
    def _check_partner_invoice_advance_payments(self):
        if self.filtered(lambda x: x.advance_payment_count and x.partner_invoice_id not in x.advance_payment_ids.partner_id):
            raise ValidationError(
                _(
                    "Sales Order has advance payments already! Cancel all the"
                    "advance payments first before changing the Invoice Address."
                )
            )

    @api.depends("amount_total", "advance_payment_ids", "advance_payment_ids.state",
                 "advance_payment_ids.move_id.line_ids.amount_residual")
    def _compute_advance_payment(self):
        for order in self:
            payments = order.sudo().advance_payment_ids.filtered(
                lambda x: x.state != 'cancel' and x.is_advance_payment
            )

            paid = 0.0
            for payment in payments.filtered(lambda x: x.state == 'posted'):
                for line in payment.move_id.line_ids.filtered(
                    lambda x: x.amount_residual != 0
                              and x.account_id.account_type == "liability_current"
                ):
                    payment_amt = payment.company_id.currency_id._convert(
                        line.amount_residual,
                        order.currency_id,
                        order.company_id,
                        payment.date,
                    )
                    paid -= payment_amt

            order.update({
                'advance_payment_count': len(payments),
                'advance_payment_amount': paid,
                'unpaid_amount': max(order.amount_total - paid, 0.0),
            })

    def _get_advance_payment_context(self):
        self.ensure_one()
        return {
            "default_advance_sale_id": self.id,
            "default_amount": self.unpaid_amount,
            "default_currency_id": self.currency_id.id,
            "default_destination_account_id": self.company_id.advance_payment_account_id.id,
            "default_is_advance_payment": True,
            "default_partner_id": self.partner_invoice_id.id,
            "default_partner_type": 'customer',
            "default_payment_type": 'inbound',
        }

    def action_view_advance_payments(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account_payment_advance_mac5.action_account_payment_advance_customer"
        )
        action["context"] = self._get_advance_payment_context()

        payments = self.advance_payment_ids
        if len(payments) > 1:
            action["domain"] = [("advance_sale_id", "=", self.id)]
        elif len(payments) == 1:
            action.update({
                "res_id": payments.id,
                "views": [x for x in action["views"] if x[1] == "form"],
            })
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def action_create_advance_payment(self):
        self.ensure_one()
        ctx = self._get_advance_payment_context()
        payment = self.env["account.payment"].with_context(ctx).create({})
        payment._onchange_journal_payment_type()

        action = self.action_view_advance_payments()
        action.update({
            "res_id": payment.id,
            "views": [x for x in action["views"] if x[1] == "form"],
        })
        return action
