# Copyright 2022-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.credit_management.tests.common import TestCreditManagementMixin


@tagged("post_install", "-at_install")
class TestCreditManagementStockPicking(TestCreditManagementMixin):
    def test_hold_picking_search(self):
        # create picking and set hold_delivery_till_payment as True.
        sale_order = self.test_create_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids[0]
        self.assertTrue(picking)
        picking.update(
            {
                "hold_delivery_till_payment": True,
            }
        )
        # Set the operator as '=' and search the records.
        # Return the record with hold_delivery_till_payment set.
        hold_delivery_till_payment_records = self.env[
            "stock.picking"
        ]._hold_picking_search(operator="=", value="hold_delivery_till_payment")[0][2]
        self.assertTrue(len(hold_delivery_till_payment_records), 1)
        # Set the operator as '!=' and search the records.
        # Return the record with hold_delivery_till_payment not set.
        non_hold_delivery_till_payment_records = self.env[
            "stock.picking"
        ]._hold_picking_search(operator="!=", value="hold_delivery_till_payment")[0][2]
        self.assertTrue(len(non_hold_delivery_till_payment_records) != 1)

    def test_compute_show_check_availability_credit_management(self):
        # Create Picking and compute the value for show_check_availability_credit_management
        sale_order = self.test_create_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids[0]
        self.assertTrue(picking)
        self.assertFalse(picking.hold_delivery_till_payment)
        picking._compute_show_check_availability_credit_management()
        self.assertFalse(picking.show_check_availability_credit_management)
        # Set the hold_delivery_till_payment in picking.
        # When Computed it will return as True
        picking.hold_delivery_till_payment = True
        picking._compute_show_check_availability_credit_management()
        self.assertTrue(picking.show_check_availability_credit_management)
        # Set the stock_allow_check_availability as True.
        # When both stock_allow_check_availability and hold_delivery_till_payment set,
        # will set the value for show_check_availability_credit_management as False
        self.config.stock_allow_check_availability = True
        self.config.execute()
        picking._compute_show_check_availability_credit_management()
        self.assertFalse(picking.show_check_availability_credit_management)

    def test_button_validate(self):
        sale_order = self.test_create_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids[0]
        self.assertTrue(picking)
        self.assertEqual(sum([line.quantity_done for line in picking.move_ids]), 0)
        picking.move_ids[0].quantity_done = picking.move_ids[0].product_uom_qty
        # Raises an error if hold_delivery_till_payment is set.
        picking.hold_delivery_till_payment = True
        self.assertTrue(picking.state, "assigned")
        with self.assertRaises(UserError), self.cr.savepoint():
            picking.button_validate()
        self.assertTrue(picking.state, "assigned")
        # Raises an error if hold_delivery_till_payment is not set and credit_hold
        # in the partner is set.
        picking.hold_delivery_till_payment = False
        picking.partner_id.commercial_partner_id.credit_hold = True
        with self.assertRaises(UserError), self.cr.savepoint():
            picking.button_validate()
        self.assertTrue(picking.state, "assigned")
        picking.partner_id.commercial_partner_id.credit_hold = False
        picking = picking.with_context(website_order_tx=True)
        # Validates the Move if credit_hold and hold_delivery_till_payment is not set.
        picking.button_validate()
        self.assertTrue(picking.state, "done")

    def test_action_confirm(self):
        sale_order = self.test_create_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids[0]
        self.assertTrue(picking)
        # Without the context hold_do the picking will not confirm if the
        # hold_delivery_till_payment is set.
        picking.hold_delivery_till_payment = True
        picking.action_confirm()
        picking = picking.with_context(hold_do=True)
        # With the context hold_do is set and hold_delivery_till_payment is True,
        # then it will raise an error.
        with self.assertRaises(UserError), self.cr.savepoint():
            picking.action_confirm()
        picking.hold_delivery_till_payment = False
        # If the partner has credit_hold then it will raise an error without
        # the context website_order_tx.
        picking.partner_id.commercial_partner_id.credit_hold = True
        with self.assertRaises(UserError), self.cr.savepoint():
            picking.action_confirm()
        picking = picking.with_context(website_order_tx=True)
        # If the partner has credit_hold and also website_order_tx is in context,
        # the order will confirm.
        picking.action_confirm()

    def test_action_assign(self):
        sale_order = self.test_create_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids[0]
        self.assertTrue(picking)
        partner = picking.partner_id.commercial_partner_id
        partner.credit_hold = True
        self.assertFalse(picking.hold_delivery_till_payment)
        with self.assertRaises(UserError), self.cr.savepoint():
            picking.action_assign()
        self.config.stock_allow_check_availability = False
        self.config.execute()
        picking.hold_delivery_till_payment = True
        partner.credit_hold = False
        picking.action_assign()
        picking.hold_delivery_till_payment = False
        picking = picking.with_context(website_order_tx=True)
        picking.action_assign()

    def test_get_moves_to_assign_domain(self):
        sale_order = self.test_create_sale_order()
        sale_order.action_confirm()
        picking = sale_order.picking_ids[0]
        self.assertTrue(picking)
        picking.hold_delivery_till_payment = True
        # Set the picking with hold_delivery_till_payment to exculde it from the search
        company_id = sale_order.company_id
        self.assertTrue(company_id)
        domain = self.env["procurement.group"]._get_moves_to_assign_domain(company_id)
        self.assertTrue(domain)
        hold_picking_id = domain[-1][2][0]
        self.assertTrue(hold_picking_id)
        self.assertTrue(picking.id, hold_picking_id)
