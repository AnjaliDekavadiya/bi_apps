# Copyright 2020-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import exception_to_unicode


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_payments_count(self):
        for order in self:
            partner = order.commercial_partner_id or order.partner_id
            order.payments_count = self.env["account.payment"].search_count(
                [
                    ("partner_id", "child_of", partner.id),
                    ("state", "in", ["draft", "posted"]),
                    # is True when 100% amount used
                    ("is_reconciled", "=", False),
                    # on the Invoices, so if it is False then it is an open payment
                ]
            )

    payments_count = fields.Integer(compute="_compute_payments_count")
    override_credit_limit = fields.Boolean(
        copy=False,
        tracking=True,
    )
    commercial_partner_id = fields.Many2one(
        "res.partner",
        related="partner_id.commercial_partner_id",
        readonly=True,
    )
    over_credit = fields.Boolean(copy=False, readonly=True)
    hold_delivery_till_payment = fields.Boolean(
        default=False,
        tracking=True,
        help="If True, then holds the DO until  \
            invoices are paid and equals to the total amount on the SO",
    )

    @api.onchange("partner_id", "payment_term_id")
    def onchange_for_hold_delivery_till_payment(self):
        for order in self:
            order.hold_delivery_till_payment = False
            if order.partner_id.hold_delivery_till_payment:
                order.hold_delivery_till_payment = True
            elif order.payment_term_id.hold_delivery_till_payment:
                order.hold_delivery_till_payment = True

    @api.onchange("partner_id")
    def onchange_partner_id_credit_warning(self):
        try:
            if self.partner_id:
                self.check_partner_credit_limit()
                self.hold_delivery_till_payment = (
                    self.partner_id.commercial_partner_id.hold_delivery_till_payment
                )
        except Exception as e:
            partner = self.partner_id.commercial_partner_id
            if (
                not partner.credit_hold
                and partner.override_credit_threshold_limit >= self.amount_total
            ):
                return
            return {
                "warning": {
                    "title": _("Warning!"),
                    "message": exception_to_unicode(e),
                }
            }

    def check_credit_limit(self, partner, prepayment_test):
        sale = self
        total_credit_used = partner.total_credit_used
        if partner.credit_hold:
            raise UserError(_("Credit Hold!\nThis Account is on hold"))
        if (
            partner.credit_limit > 0 or prepayment_test
        ) and not sale.override_credit_limit:
            if sale.payment_method_id and not sale.payment_method_id.prepayment_test:
                return

            if (
                total_credit_used == 0
                and partner.credit_limit == 0
                and not prepayment_test
            ):
                return

            if (total_credit_used >= partner.credit_limit) or (
                sale.state != "sale"
                and total_credit_used + sale.amount_total > partner.credit_limit
            ):
                raise UserError(
                    _(
                        """Over Credit Limit!\n
                        Credit Limit: %(symbol)s%(credit_limit)s\n
                        Total Credit Balance: %(symbol)s%(total_credit_used)s\n
                        Total this order: %(symbol)s%(amount_total)s"""
                    )
                    % {
                        "symbol": sale.currency_id.symbol,
                        "credit_limit": partner.credit_limit,
                        "total_credit_used": total_credit_used,
                        "amount_total": sale.amount_total,
                    }
                )

    def check_partner_credit_limit(self):
        if not self._context.get("website_order_tx", False):
            prepayment_test = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("credit_management.prepayment_test", False)
            )
            no_of_days_overdue_test = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("credit_management.no_of_days_overdue_test", False)
            )
            for sale in self:
                # credit limit check
                if not sale.company_id.is_partner_credit:
                    continue
                commercial_partner_id = sale.partner_id.commercial_partner_id
                if sale.partner_id.individual_credit_limit:
                    sale.check_credit_limit(sale.partner_id, prepayment_test)
                sale.check_credit_limit(commercial_partner_id, prepayment_test)
                if (
                    no_of_days_overdue_test
                    and commercial_partner_id.has_overdue_by_x_days
                    and not sale.override_credit_limit
                ):
                    raise UserError(
                        _("Overdue Invoices! %s has overdue invoices.")
                        % commercial_partner_id.name
                    )

    def action_confirm(self):
        if not self.env.context.get("credit_management_by_approval_process", False):
            for order in self:
                partner = order.partner_id.commercial_partner_id
                if order.hold_delivery_till_payment:
                    continue
                try:
                    order.over_credit = False
                    order.check_partner_credit_limit()
                except UserError as e:
                    if not partner.credit_hold:
                        order.over_credit = True
                    if (
                        not partner.credit_hold
                        and partner.override_credit_threshold_limit
                        >= order.amount_total
                    ):
                        res = super(SaleOrder, order).action_confirm()
                        order.override_credit_limit = True
                        return res
                    return {
                        "name": "Credit Limit Warning",
                        "type": "ir.actions.act_window",
                        "res_model": "partner.credit.limit.warning",
                        "view_mode": "form",
                        "view_type": "form",
                        "target": "new",
                        "context": {"default_message": exception_to_unicode(e)},
                    }
        return super().action_confirm()

    def open_payments(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.pop("group_by", None)
        ctx.update(
            {
                "default_payment_type": "inbound",
                "default_partner_id": self.partner_id.id,
                "default_journal_id": self.payment_method_id.id,
                "default_amount": self.amount_total,
                "sale_ids": self.ids,
            }
        )
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_account_payments"
        )
        if action:
            partner = self.commercial_partner_id or self.partner_id
            action["context"] = ctx
            action["domain"] = [
                ("partner_id", "child_of", partner.id),
                ("state", "in", ["draft", "posted"]),
                ("is_reconciled", "=", False),
            ]
            return action

    def action_cancel(self):
        res = super().action_cancel()
        self.write(
            {
                "over_credit": False,
                "override_credit_limit": False,
            }
        )
        return res

    def check_invoice_fully_paid(self):
        self.ensure_one()
        downpayment_invoices = (
            self.mapped("order_line")
            .filtered(lambda x: x.is_downpayment)
            .invoice_lines.mapped("move_id")
            .filtered(lambda x: x.move_type == "out_invoice")
        )
        downpayment_amount = self.get_invoice_total_amount(downpayment_invoices)
        invoice_amount = self.get_invoice_total_amount(
            self.invoice_ids.filtered(lambda x: x.move_type == "out_invoice")
        )
        if (
            invoice_amount >= self.amount_total
            or downpayment_amount >= self.amount_untaxed
        ):
            return True
        else:
            return False

    @api.model
    def get_invoice_total_amount(self, invoices):
        total_amount = 0.0
        for invoice in invoices:
            (
                invoice_partials,
                exchange_diff_moves,
            ) = invoice._get_reconciled_invoices_partials()
            for invoice_partial in invoice_partials:
                for (
                    _partial,
                    _amount,
                    counterpart_line,
                ) in invoice_partial:
                    if (
                        counterpart_line.payment_id.payment_method_id.code
                        == "batch_payment"
                        and invoice.payment_state in ["in_payment", "paid"]
                        and counterpart_line.payment_id.is_matched
                    ):
                        total_amount += counterpart_line.payment_id.amount
                    elif (
                        counterpart_line.payment_id.payment_method_id.code
                        != "batch_payment"
                        and invoice.payment_state in ["in_payment", "paid"]
                    ):
                        total_amount += counterpart_line.payment_id.amount
        return total_amount
