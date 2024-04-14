# Copyright 2022-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo.tests.common import TransactionCase


class TestCreditManagementMixin(TransactionCase):
    def setUp(self):
        super().setUp()
        self.config = self.env["res.config.settings"].create({})
        self.config.add_prepayment_test = False
        self.config.no_of_days_overdue_test = False
        self.config.x_no_of_overdue_days = 3
        self.config.stock_allow_check_availability = False
        self.config.execute()
        self.payment_method_id = self.env["account.journal"].create(
            {
                "name": "Bank US",
                "type": "bank",
                "code": "BNK68",
                "currency_id": self.env.ref("base.USD").id,
                "prepayment_test": False,
            }
        )
        partner_values = {"name": "Imperator Caius Julius Caesar Divus"}
        self.partner = self.env["res.partner"].create(partner_values)
        product_values = {
            "name": "Bread",
            "list_price": 5,
            "type": "product",
            "categ_id": self.env.ref("product.product_category_all").id,
        }
        self.product = self.env["product.product"].create(product_values)

    def test_create_sale_order(self):
        sale_obj = self.env["sale.order"]
        partner = self.partner
        product = self.product
        self.product_uom_unit = self.env.ref("uom.product_uom_unit")
        pricelist_id = self.env["product.pricelist"].create(
            {
                "name": "default_pricelist",
                "currency_id": 1,
            }
        )
        values = {
            "pricelist_id": pricelist_id.id,
            "partner_id": partner.id,
            "payment_term_id": self.env.ref(
                "account.account_payment_term_end_following_month"
            ).id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": product.id,
                        "product_uom": self.product_uom_unit.id,
                        "price_unit": self.product.list_price,
                        "product_uom_qty": 1,
                    },
                )
            ],
        }
        order = sale_obj.create(values)
        # Create inventory
        for line in order.order_line:
            if line.product_id.type == "product":
                inventory = self.env["stock.quant"].create(
                    {
                        "product_id": line.product_id.id,
                        "location_id": self.env.ref("stock.stock_location_stock").id,
                        "inventory_quantity": line.product_uom_qty,
                    }
                )
                inventory._apply_inventory()
        return order

    def validate_picking(self, sale_order):
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(
            sum([line.quantity_done for line in sale_order.picking_ids.move_ids]), 0
        )
        sale_order.picking_ids.move_ids[
            0
        ].quantity_done = sale_order.picking_ids.move_ids[0].product_uom_qty
        sale_order.picking_ids.button_validate()
        self.assertEqual(sale_order.picking_ids[0].state, "done")
        self.assertEqual(
            sum([line.quantity_done for line in sale_order.picking_ids.move_ids]),
            sale_order.picking_ids.move_ids[0].product_uom_qty,
        )

    def post_invoice(self, invoice, sale_order):
        self.assertTrue(invoice.id in sale_order.invoice_ids.ids)
        self.assertTrue(invoice)
        self.assertEqual(invoice.state, "draft")
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
        self.assertEqual(invoice.move_type, "out_invoice")
        self.assertEqual(invoice.payment_state, "not_paid")
