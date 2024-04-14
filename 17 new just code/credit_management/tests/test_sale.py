# Copyright 2022-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.credit_management.tests.common import TestCreditManagementMixin


@tagged("post_install", "-at_install")
class TestCreditManagementSale(TestCreditManagementMixin):
    def test_compute_payments_count(self):
        # Creating Sale Order to test the compute_payments_count in SO.
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        # Confirm the Sale Order and deliver the Products
        sale_order.action_confirm()
        self.validate_picking(sale_order)
        # Invoice the Delivered Products and Post
        invoice = sale_order._create_invoices()
        self.post_invoice(invoice, sale_order)
        # Compute the Value of Payments available in the Sale Order.
        sale_order._compute_payments_count()
        self.assertEqual(sale_order.payments_count, 0)
        # Create Payment for the Invoice and Reconcile it.
        payments = (
            self.env["account.payment.register"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create(
                {
                    "payment_date": fields.Date.from_string(fields.Date.today()),
                }
            )
            ._create_payments()
        )
        self.assertTrue(payments)
        self.assertTrue(payments.is_reconciled)
        payments.is_reconciled = False
        # Unreconcile and Compute the Payments available for the Sale Order.
        sale_order._compute_payments_count()
        self.assertTrue(sale_order.payments_count > 0)

    def test_hold_delivery_till_payment(self):
        self.assertFalse(self.partner.hold_delivery_till_payment)
        # Create Sale Order
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        self.assertTrue(sale_order.payment_term_id)
        self.assertFalse(sale_order.hold_delivery_till_payment)
        # Set the Hold Delivery Boolean on Payment Term
        sale_order.payment_term_id.hold_delivery_till_payment = True
        sale_order.onchange_for_hold_delivery_till_payment()
        self.assertTrue(sale_order.hold_delivery_till_payment)
        sale_order.hold_delivery_till_payment = False
        sale_order.partner_id.hold_delivery_till_payment = True
        sale_order.onchange_for_hold_delivery_till_payment()
        self.assertTrue(sale_order.hold_delivery_till_payment)

    def test_onchange_partner_id_credit_warning(self):
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        partner = sale_order.partner_id.commercial_partner_id
        partner.hold_delivery_till_payment = True
        sale_order.onchange_partner_id_credit_warning()
        self.assertTrue(
            partner.hold_delivery_till_payment, sale_order.hold_delivery_till_payment
        )
        self.config.no_of_days_overdue_test = True
        self.config.execute()
        partner.has_overdue_by_x_days = True
        sale_order.onchange_partner_id_credit_warning()
        partner.override_credit_threshold_limit = 10
        sale_order.onchange_partner_id_credit_warning()

    def test_partner_credit_limit(self):
        self.config.add_prepayment_test = True
        self.config.execute()
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        sale_order.override_credit_limit = False
        partner = sale_order.partner_id.commercial_partner_id
        partner.commercial_partner_id.credit_hold = True
        with self.assertRaises(UserError), self.cr.savepoint():
            sale_order.check_partner_credit_limit()
        partner.commercial_partner_id.credit_hold = False
        sale_order.payment_method_id = self.payment_method_id.id
        self.assertTrue(sale_order.payment_method_id)
        sale_order.check_partner_credit_limit()
        sale_order.payment_method_id.prepayment_test = True
        self.config.add_prepayment_test = False
        self.config.execute()
        partner.credit_limit = 100
        partner.commercial_partner_id.total_credit_used = 101
        self.assertTrue(partner.total_credit_used > partner.credit_limit)
        with self.assertRaises(UserError), self.cr.savepoint():
            sale_order.check_partner_credit_limit()
        partner.commercial_partner_id.total_credit_used = 99
        self.assertTrue(
            partner.total_credit_used + sale_order.amount_total > partner.credit_limit
        )
        with self.assertRaises(UserError), self.cr.savepoint():
            sale_order.check_partner_credit_limit()
        self.config.no_of_days_overdue_test = True
        self.config.execute()
        partner.has_overdue_by_x_days = True
        with self.assertRaises(UserError), self.cr.savepoint():
            sale_order.check_partner_credit_limit()

    def test_action_confirm(self):
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        partner = sale_order.partner_id.commercial_partner_id
        sale_order.hold_delivery_till_payment = True
        sale_order.action_confirm()
        self.assertTrue(sale_order.state != "draft")
        sale_order.hold_delivery_till_payment = False
        partner.credit_hold = True
        sale_order.action_confirm()
        partner.credit_hold = False
        partner.override_credit_threshold_limit = 150
        self.config.no_of_days_overdue_test = True
        self.config.execute()
        partner.has_overdue_by_x_days = True
        sale_order.override_credit_limit = False
        sale_order.action_confirm()
        self.assertTrue(sale_order.override_credit_limit, True)
        self.assertTrue(sale_order.state, "sale")

    def test_open_payments(self):
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        partner = sale_order.partner_id.commercial_partner_id
        payment = self.env["account.payment"].create(
            {
                "amount": sale_order.amount_total,
                "payment_type": "outbound",
                "partner_type": "customer",
                "partner_id": partner.id,
            }
        )
        self.assertTrue(payment)
        self.assertTrue(payment.state, "draft")
        self.assertFalse(payment.is_reconciled)
        sale_order.open_payments()

    def test_action_cancel(self):
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        self.assertTrue(sale_order.state, "draft")
        sale_order.over_credit = True
        sale_order.override_credit_limit = True
        # write the values of over_credit and override_credit_limit as False if cancelled
        sale_order.action_cancel()
        self.assertFalse(sale_order.over_credit)
        self.assertFalse(sale_order.override_credit_limit)

    def test_check_invoice_fully_paid(self):
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        old_price = sale_order.order_line[0].price_unit
        sale_order.order_line[0].update(
            {
                "price_unit": 150,
            }
        )
        new_price = sale_order.order_line[0].price_unit
        self.assertTrue(new_price > old_price)
        sale_order.action_confirm()
        self.assertTrue(sale_order.state, "sale")
        so_context = {
            "active_model": "sale.order",
            "active_ids": [sale_order.id],
            "active_id": sale_order.id,
        }
        # Create a downpayment invoice for the sale order to check if the invoice is fully paid.
        # Returns False if the payment on the invoice is less than the amount_total of invoice
        downpayment = (
            self.env["sale.advance.payment.inv"]
            .with_context(**so_context)
            .create(
                {
                    "advance_payment_method": "percentage",
                    "amount": 50,
                }
            )
        )
        downpayment.create_invoices()
        invoice = sale_order.invoice_ids[0]
        self.assertTrue(invoice)
        self.post_invoice(invoice, sale_order)
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create(
            {
                "payment_date": invoice.date,
            }
        )._create_payments()
        self.assertTrue(invoice.payment_state, "in_payment")
        self.assertFalse(sale_order.check_invoice_fully_paid())
        # Create another Invoice with remaining amount for the Sale Order.
        downpayment_1 = (
            self.env["sale.advance.payment.inv"]
            .with_context(**so_context)
            .create(
                {
                    "advance_payment_method": "percentage",
                    "amount": 50,
                }
            )
        )
        downpayment_1.create_invoices()
        invoice = sale_order.invoice_ids[1]
        self.assertTrue(invoice)
        self.post_invoice(invoice, sale_order)
        # Create Payment for the invoice with amount of invoice.amount_total
        # This will return True since the amount_total of Invoice = Payment Amount.
        # This will also return True when the downpayment_amount \
        # >= amount_untaxed of the Invoice.
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create(
            {
                "amount": invoice.amount_total,
                "payment_date": invoice.date,
            }
        )._create_payments()
        self.assertTrue(invoice.payment_state, "in_payment")
        self.assertTrue(sale_order.check_invoice_fully_paid())
        # Change the values of the payment related to the credit lines of the invoice.
        # calculate the total_amount for the Batch Payments
        pay_term_lines = invoice.line_ids.filtered(
            lambda line: line.account_type in ("asset_receivable", "liability_payable")
        )
        self.assertTrue(pay_term_lines)
        payment_id = pay_term_lines.matched_credit_ids.credit_move_id.payment_id
        self.assertTrue(payment_id)
        payment_id.payment_method_id.code = "batch_payment"
        payment_id.is_matched = True
        sale_order.check_invoice_fully_paid()
