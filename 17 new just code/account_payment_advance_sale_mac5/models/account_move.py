from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(AccountMove, self).action_post()

        for invoice in self.filtered(lambda i: i.move_type == "out_invoice"):
            if not invoice.company_id.advance_payment_journal_id:
                raise ValidationError(_("Setup the Advance Payment Journal first!"))

            for payment in invoice.line_ids.sale_line_ids.order_id.advance_payment_ids:
                if payment.state != "posted":
                    continue
                if (payment.partner_id == invoice.partner_id and invoice.amount_residual > 0.0
                        and payment.residual > 0.0):
                    wiz = self.env["account.advance.payment.invoice"].with_context({
                        "active_model": "account.move",
                        "active_ids": invoice.ids,
                    }).create({
                        "advance_payment_ids": [(6, 0, payment.ids)],
                        "date": max(invoice.invoice_date, payment.date),
                        "journal_id": invoice.company_id.advance_payment_journal_id.id,
                    })
                    wiz.apply_advance_payment()
        return res
