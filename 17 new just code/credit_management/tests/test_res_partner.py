# Copyright 2022-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from datetime import timedelta

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.credit_management.tests.common import TestCreditManagementMixin


@tagged("post_install", "-at_install")
class TestCreditManagementResPartner(TestCreditManagementMixin):
    def test_overdue_invoices(self):
        partner = self.partner
        has_overdue_by_x_days = partner.has_overdue_by_x_days
        self.assertFalse(has_overdue_by_x_days)
        today = fields.Date.from_string(fields.Date.today())
        # Create Invoice
        invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": partner.id,
                    "date": today,
                    "invoice_date": today,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "product_id": self.product.id,
                            }
                        )
                    ],
                }
            ]
        )
        self.assertTrue(invoice)
        partner._compute_check_overdue_invoices()
        self.assertFalse(partner.has_overdue_by_x_days)
        # Post the Invoice to get the number of Overdue Days.
        invoice.action_post()
        date_due = fields.Date.from_string(invoice.invoice_date_due)
        invoice.invoice_date_due = date_due - timedelta(days=5)
        self.assertTrue(invoice.invoice_date_due < today)
        # Returns True if the partner has overdue invoice.
        has_overdue_by_x_days = partner._compute_check_overdue_invoices()
        self.assertTrue(partner.has_overdue_by_x_days)

    def test_total_credit_used(self):
        partner = self.partner
        has_overdue_by_x_days = partner.has_overdue_by_x_days
        self.assertFalse(has_overdue_by_x_days)
        # Creating the Sale Order and then Invoice to test the draft Invoices
        # having Order Line and Move Line Relation
        sale_order = self.test_create_sale_order()
        self.assertTrue(sale_order)
        # confirm the Sale Order and Deliver the Product
        sale_order.action_confirm()
        self.validate_picking(sale_order)
        # Invoice the Delivered Products
        invoice = sale_order._create_invoices()
        # Compute the Credit Used for SO.
        partner._compute_get_total_credit_used()
        self.assertTrue(partner.total_credit_used > 0.0)
        self.post_invoice(invoice, sale_order)
        # total_credit_used will be returned as 0.0 if we compute
        partner.active = False
        partner._compute_get_total_credit_used()
        self.assertEqual(partner.total_credit_used, 0.0)
