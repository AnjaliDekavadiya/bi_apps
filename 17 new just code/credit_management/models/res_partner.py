# Copyright 2020-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    credit_limit = fields.Float(groups=None)
    has_overdue_by_x_days = fields.Boolean(
        string="Has Overdue Invoices",
        compute="_compute_check_overdue_invoices",
        help="Has overdue invoices by x no of days",
    )
    override_credit_threshold_limit = fields.Integer(
        string="Override credit Threshold",
        help="Below a specified amount, orders will automatically override the credit limit",
    )
    hold_delivery_till_payment = fields.Boolean(
        default=False,
        copy=False,
        help="If True, then holds the DO until  \
                                    invoices are paid and equals to the total amount on the SO",
    )
    individual_credit_limit = fields.Boolean(
        string="Manage Individual Credit Limit",
    )

    def _compute_check_overdue_invoices(self):
        account_move_sudo = self.env["account.move"].sudo()
        x_no_of_overdue_days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("credit_management.x_no_of_overdue_days", default=0)
        )
        for partner in self:
            for invoice in account_move_sudo.search(
                [
                    ("partner_id", "child_of", partner.commercial_partner_id.id),
                    ("state", "=", "posted"),
                    ("move_type", "=", "out_invoice"),
                    ("payment_state", "in", ("partial", "not_paid")),
                    ("invoice_date_due", "!=", False),
                    ("invoice_date_due", "<", fields.Date.today()),
                ]
            ):
                date_due = fields.Date.from_string(invoice.invoice_date_due)
                today = fields.Date.from_string(fields.Date.today())
                delta = date_due - today
                if abs(delta.days) > x_no_of_overdue_days:
                    partner.has_overdue_by_x_days = True
                    break
            else:
                partner.has_overdue_by_x_days = False

    def _compute_get_total_credit_used(self):
        commercial_partner_processed = []
        for partner in self:
            partner.total_credit_used = 0.0
            original_partner = partner
            if partner.id in commercial_partner_processed:
                continue  # compute already done for this partner
            commercial_partner_processed.append(original_partner.id)
            if partner.commercial_partner_id:
                partner = partner.commercial_partner_id
                commercial_partner_processed.append(partner.id)
            if not isinstance(partner.id, models.NewId):
                if not partner.active:
                    continue
                child_ids = tuple(self.search([("id", "child_of", partner.id)]).ids)

                not_invoiced_order_lines_query = """
                    select sum(
                        CASE
                            WHEN (sol.qty_invoiced >= 0) and
                                (sol.product_uom_qty - sol.qty_invoiced) > 0
                            THEN ((sol.product_uom_qty - sol.qty_invoiced) *
                            (sol.price_unit + (sol.price_tax / sol.product_uom_qty)))
                            ELSE 0
                        END
                    )
                    from
                        sale_order_line sol, sale_order so
                    where
                        sol.order_id = so.id and
                        sol.order_partner_id in %s
                        and sol.state in %s
                        and sol.invoice_status != %s
                        and sol.company_id = %s
                """

                if "active" in self.env["sale.order"]._fields:
                    not_invoiced_order_lines_query += " and so.active=True"

                self._cr.execute(
                    not_invoiced_order_lines_query,
                    (child_ids, ("sale", "done"), "invoiced", self.env.company.id),
                )
                amount_not_invoiced_order_lines = self._cr.dictfetchone()["sum"] or 0.0

                invoiced_downpayment_lines_query = """
                select sum(sol.price_total) from sale_order_line sol, sale_order so
                where
                sol.order_id = so.id and
                sol.order_partner_id in %s and
                sol.state in %s and
                sol.is_downpayment = %s and
                sol.qty_invoiced != %s and
                sol.company_id = %s
                """

                if "active" in self.env["sale.order"]._fields:
                    invoiced_downpayment_lines_query += " and so.active=True"

                self._cr.execute(
                    invoiced_downpayment_lines_query,
                    (child_ids, ("sale", "done"), "true", 0, self.env.company.id),
                )
                amount_invoiced_downpayment_lines = (
                    self._cr.dictfetchone()["sum"] or 0.0
                )

                confirmed_so_not_invoiced = (
                    amount_not_invoiced_order_lines - amount_invoiced_downpayment_lines
                )

                draft_invoice_query = """
                select distinct(am.id),
                am.amount_total from account_move_line aml,
                sale_order_line_invoice_rel sol_rel,
                account_move am
                where aml.partner_id in %s and
                sol_rel.invoice_line_id = aml.id and
                am.id = aml.move_id and
                am.state = %s and
                am.move_type != %s and
                am.move_type != %s and
                am.company_id = %s
                """
                self._cr.execute(
                    draft_invoice_query,
                    (child_ids, "draft", "entry", "out_refund", self.env.company.id),
                )
                draft_invoices = self._cr.fetchall()
                draft_invoices_amount = 0.0
                for draft_invoice in draft_invoices:
                    draft_invoices_amount += draft_invoice[1]

                partner.total_credit_used = (
                    partner.credit + confirmed_so_not_invoiced + draft_invoices_amount
                )
                original_partner.total_credit_used = partner.total_credit_used

    total_credit_used = fields.Monetary(
        compute="_compute_get_total_credit_used",
        help="Total credit used by the partner",
    )
    credit_hold = fields.Boolean(
        help="True, if the credit is on hold",
        tracking=True,
        copy=False,
    )
