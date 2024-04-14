import base64
import csv
from datetime import datetime
import logging
import time
from io import StringIO

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


_logger = logging.getLogger(__name__)


class AmazonReportLog(models.Model):
    _inherit = "amazon.report.log"

    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        relation="sale_order_amazon_report_log_rel",
        column1="report_log_id", column2="sale_order_id",
        string="Sale Orders", readonly=True, copy=False,
    )
    sale_count = fields.Integer(compute='_compute_sale_count')
    synchronization_log_ids = fields.One2many(
        comodel_name="amazon.synchronization.log",
        inverse_name="report_log_id", string="Synchronization Logs",
        readonly=True
    )
    fba_stock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="fba_stock_report_id",
        string="FBA Live Stock Moves",
        readonly=True
    )
    ticket_ids = fields.One2many(
        comodel_name="helpdesk.ticket",
        inverse_name="fba_return_report_id",
        string="FBA Return Tickets",
        readonly=True
    )
    sync_log_count = fields.Integer(compute='_compute_sync_log_count')
    statement_id = fields.Many2one("account.bank.statement", string="Statement")

    @api.depends('sale_order_ids')
    def _compute_sale_count(self):
        for report in self:
            report.sale_count = len(report.sale_order_ids)
    @api.depends('synchronization_log_ids')
    def _compute_sync_log_count(self):
        for report in self:
            report.sync_log_count = len(report.synchronization_log_ids)

    def action_view_sale_orders(self):
        action = self.env['ir.actions.actions']._for_xml_id('sale.action_orders')
        action["domain"] = [('id', 'in', self.sale_order_ids.ids)]
        return action

    def action_view_sync_logs(self):
        action = self.env['ir.actions.actions']._for_xml_id('amazon_connector_base.amazon_sync_log_action')
        action["domain"] = [('id', 'in', self.synchronization_log_ids.ids)]
        return action

    @api.model
    def order_create_invoicing_partner(self, order_id, row):
        sale_env = self.env["sale.order"]
        order = sale_env.search([('amazon_order_ref', '=', order_id)])
        if order.partner_invoice_id != order.partner_id:
            return False
        partner_env = self.env["res.partner"]
        state_env = self.env["res.country.state"]
        country_env = self.env["res.country"]
        invoice_partner_vals = {
            "parent_id": order.partner_id.id,
            "type": "invoice",
            "name": row.get("billing-name", row["buyer-name"]),
            "phone": row.get("billing-phone-number", row["buyer-phone-number"]),
            "street": row["bill-address-1"],
            "street2": row["bill-address-2"],
            "city": row["bill-city"],
            "zip": row["bill-postal-code"],
            "vat": row.get("buyer-vat-number", False),
        }
        state = state_env.search([("name", "=", row["bill-state"])])
        if len(state) == 1:
            invoice_partner_vals["state_id"] = state.id
        country = country_env.search([("code", "=", row["bill-country"])])
        if country:
            invoice_partner_vals["country_id"] = country.id
        invoice_partner = partner_env.with_context(
            tracking_disable=True).create(invoice_partner_vals)
        order.write({
            "partner_invoice_id": invoice_partner.id,
        })
        return True

    def process_report_GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT(self):
        imp_file = StringIO(base64.b64decode(self.report_file).decode())
        reader = csv.DictReader(imp_file, delimiter="\t")
        sale_env = self.env["sale.order"]
        sale_line_env = self.env["sale.order.line"]
        country_env = self.env["res.country"]
        sync_log_env = self.env["amazon.synchronization.log"]
        so_lines = self.env["sale.order.line"]
        orders_dict = {}
        for row in reader:
            order_date = fields.Datetime.from_string(row["order-date"])
            if order_date < datetime(2023, 8, 1, 0, 0, 0):
                continue
            if row["order-id"] not in orders_dict:
                orders_dict[row["order-id"]] = []
            orders_dict[row["order-id"]].append(row)
        orders_to_import = []
        for order_ref in orders_dict:
            # Loop 2nd time to avoid duplicate searching
            order = sale_env.search([('amazon_order_ref', '=', order_ref)])
            if not order:
                orders_to_import.append(order_ref)
        sale_env.bulk_import_amazon_orders(self.account_id, orders_to_import)

        rows = []
        for order_id, row in orders_dict.items():
            rows += row
            self.order_create_invoicing_partner(order_id, row[0])

        for row in rows:
            domain_search = [
                ("order_id.amazon_order_ref", "=", row["order-id"]),
                ("amazon_item_ref", "=", row["legacy-customer-order-item-id"]),
                # '|', ("amz_shipment_id", "=", False),
                # ("amz_shipment_id", "=", row["shipping-id"]),
            ]
            shipment_date = fields.Datetime.from_string(row["shipment-date"])
            if shipment_date < datetime(2023, 8, 1, 0, 0, 0):
                continue
            if row["transaction-type"] != "SHIPMENT":
                domain_search.append(
                    # ("amz_transaction_inv_id", "=", row["transaction-id"]),
                    ("amz_shipment_id", "=", row["shipping-id"]),
                )
                # continue
            so_line = sale_line_env.search(domain_search, order="id ASC", limit=1)
            if not so_line:
                _logger.info("No sale order line found for row %s" % row)
                sync_log_env.create({
                    'account_id': self.account_id.id,
                    'operation_type': 'import_order',
                    'log_type': 'not_found',
                    'message': "No sale order line found for row %s" % row["legacy-customer-order-item-id"],
                    'user_id': self.env.user.id,
                    'amazon_order_ref': row["order-id"],
                    'report_log_id': self.id,
                    "json_debug": str(row),
                })
                continue
                # sale_env.import_amazon_order(self.account_id, row["order-id"])
                # time.sleep(1)
                # so_line = sale_line_env.search(domain_search, order="id ASC", limit=1)
            if so_line.amz_shipment_id == row["shipping-id"]:
                if row["transaction-type"] != "SHIPMENT":
                    so_line.write({
                        "amz_transaction_refund_id": row["transaction-id"],
                    })
                continue
            total_net_line_amount = sum([
                float(row["item-vat-excl-amount"]), float(row["item-promo-vat-excl-amount"]),
                float(row["gift-wrap-vat-excl-amount"]), float(row["gift-promo-vat-excl-amount"]),
                float(row["shipping-vat-excl-amount"]), float(row["shipping-promo-vat-excl-amount"]),
            ])
            total_tax_line_amount = sum([
                float(row["item-vat-amount"]), float(row["item-promo-vat-amount"]),
                float(row["gift-wrap-vat-amount"]), float(row["gift-promo-vat-amount"]),
                float(row["shipping-vat-amount"]), float(row["shipping-promo-vat-amount"]),
            ])
            purchased_qty = int(row["quantity-purchased"])
            vals = {
                "amz_shipment_id": row["shipping-id"],
                "amz_shipment_date": shipment_date,
                "item_promotion_id": row["item-promotion-id"],
                "ship_promotion_id": row["ship-promotion-id"],
                "ship_from_address": "%s %s, %s " % (
                    row["ship-from-postal-code"],
                    row["ship-from-city"],
                    row["ship-from-state"],
                ),
                "ship_from_country_id": country_env.search([
                    ("code", "=", row["ship-from-country"])]).id,
                "amz_total_net_line_amount": total_net_line_amount,
                "amz_total_tax_line_amount": total_tax_line_amount,
            }
            if row["transaction-type"] == "SHIPMENT":
                vals["amz_transaction_inv_id"] = row["transaction-id"]
            else:
                vals["amz_transaction_refund_id"] = row["transaction-id"]

            # Search for any additional SO lines
            additional_lines = sale_line_env.search([
                ("id", "!=", so_line.id),
                ("order_id.amazon_order_ref", "=", row["order-id"]),
                ("amazon_item_ref", "like", row["legacy-customer-order-item-id"]),
            ])
            if additional_lines:
                additional_lines.write({
                    "amz_shipment_id": vals["amz_shipment_id"],
                    "ship_from_country_id": vals["ship_from_country_id"],
                    "amz_transaction_inv_id": vals["amz_transaction_inv_id"],
                    "amz_transaction_refund_id": vals.get("amz_transaction_refund_id"),
                })

            if (row["transaction-type"] == "SHIPMENT" and
                    so_line.ship_from_country_id and
                    so_line.ship_from_country_id.id != vals["ship_from_country_id"]
                ):
                # Have to split the lines
                new_vals = vals.copy()
                new_vals.update({
                    "amazon_item_ref": "%s-%s" % (so_line.amazon_item_ref, vals["amz_shipment_id"]),
                    "price_unit": so_line.price_unit,
                    "product_uom_qty": purchased_qty,
                    "order_id": so_line.order_id.id,
                })
                so_line.write({
                    "price_unit": so_line.price_unit,
                    "product_uom_qty": (so_line.product_uom_qty -
                        int(new_vals["product_uom_qty"]))
                })
                new_so_line = so_line.copy(default=new_vals)
                new_so_line.with_context(
                    origin_country_id=vals["ship_from_country_id"])._compute_tax_id()
                so_lines |= new_so_line
                continue
            so_line.write(vals)
            # so_line.flush_recordset(["amz_shipment_id"])
            # so_line.with_context(
            #     origin_country_id=vals["ship_from_country_id"])._compute_tax_id()
            so_lines |= so_line
            if row['is-business-order'] == 'true' and not so_line.order_id.is_amz_business_order:
                so_line.order_id.write({
                    "is_amz_business_order": True
                })
            if row["buyer-vat-number"] and not so_line.order_id.partner_invoice_id.vat:
                so_line.order_id.partner_invoice_id.write({
                    "vat": row["buyer-vat-number"]
                })
        sale_orders = so_lines.mapped("order_id")
        self.write({
            "sale_order_ids": [(4, so_id) for so_id in sale_orders.ids],
        })
        self.env.cr.commit()

        draft_so = self.env["sale.order"]
        for so in self.sale_order_ids:
            # so.write({
            #     "need_to_push_pdf_invoice": True
            # })
            if so.amazon_channel != "fba":
                continue
            self.account_id._generate_stock_moves(so)
            if so.state == "draft":
                draft_so |= so
        draft_so.write({'state': 'done'})

        # self.env.cr.commit()
        wiz_env = self.env["sale.advance.payment.inv"]
        for so in self.sale_order_ids:
            lines_to_inv = so.order_line.filtered(lambda l: l.amz_transaction_inv_id and not l.invoice_lines)
            if not lines_to_inv:
                # Nothing to invoice
                continue
            try:
                so_inv = wiz_env.create({
                    "sale_order_ids": [(6, 0, [so.id])]
                })
                so_inv.create_invoices()
            except UserError as error:
                sync_log_env.create({
                    'account_id': self.account_id.id,
                    'operation_type': 'import_order',
                    'log_type': 'error',
                    'message': "Error when creating invoice for SO %s:\n%s" % (so, error),
                    'user_id': self.env.user.id,
                    'amazon_order_ref': so.amazon_order_ref,
                    'report_log_id': self.id,
                    #"json_debug": str(row),
                })

        self.sale_order_ids.mapped("invoice_ids").filtered(
            lambda inv: inv.state == "draft").action_post()
        return True

    def process_report_GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING(self):
        imp_file = StringIO(base64.b64decode(self.report_file).decode())
        reader = csv.DictReader(imp_file, delimiter="\t")
        sale_env = self.env["sale.order"]
        sale_line_env = self.env["sale.order.line"]
        fc_env = self.env["amazon.fulfillment.center"]
        sync_log_env = self.env["amazon.synchronization.log"]
        so_lines = self.env["sale.order.line"]
        orders_dict = {}
        for row in reader:
            if row["purchase-date"]:
                order_date = datetime.strptime(row["purchase-date"][:19], "%Y-%m-%dT%H:%M:%S")
                if order_date < datetime(2023, 8, 1, 0, 0, 0):
                    continue
            if row["sales-channel"] not in ["Amazon.co.uk", "Non-Amazon"]:
                continue
            order_id = row["amazon-order-id"]
            if row["merchant-order-id"]:
                order_id = row["merchant-order-id"]
            if order_id not in orders_dict:
                orders_dict[order_id] = []
            orders_dict[order_id].append(row)
        orders_to_import = []
        for order_ref in orders_dict:
            # Loop 2nd time to avoid duplicate searching
            if not sale_env.search([('name', '=', order_ref)]):
                orders_to_import.append(order_ref)
        sale_env.bulk_import_amazon_orders(self.account_id, orders_to_import)

        rows = []
        for order_id, row in orders_dict.items():
            rows += row
            self.order_create_invoicing_partner(order_id, row[0])

        for row in rows:
            order_id = row["amazon-order-id"]
            if row["merchant-order-id"]:
                order_id = row["merchant-order-id"]
            domain_search = [
                ("order_id.name", "=", order_id),
                # '|', ("amz_shipment_id", "=", False),
                # ("amz_shipment_id", "=", row["shipping-id"]),
            ]
            if row["sales-channel"] == "Non-Amazon":
                domain_search.append(
                    ("product_id.default_code", "=", row["merchant-order-item-id"])
                )
            else:
                domain_search.append(
                    ("amazon_item_ref", "=", row["amazon-order-item-id"])
                )

            shipment_date = datetime.strptime(row["shipment-date"][:19], "%Y-%m-%dT%H:%M:%S")
            if shipment_date < datetime(2023, 8, 1, 0, 0, 0):
                continue
            so_line = sale_line_env.search(domain_search, order="id ASC", limit=1)
            if not so_line:
                _logger.info("No sale order line found for row %s" % row)
                sync_log_env.create({
                    'account_id': self.account_id.id,
                    'operation_type': 'import_order',
                    'log_type': 'not_found',
                    'message': "No sale order line found for row %s" % (
                        row["merchant-order-item-id"] or row["amazon-order-item-id"]
                    ),
                    'user_id': self.env.user.id,
                    'amazon_order_ref': order_id,
                    'report_log_id': self.id,
                    "json_debug": str(row),
                })
                continue
            if row["sales-channel"] == "Non-Amazon":
                so_line.order_id.write({"amazon_order_ref": row["amazon-order-id"]})
            if so_line.amz_shipment_id == row["shipment-id"]:
                continue
            total_net_line_amount = sum([
                float(row["item-price"] or "0.00"), float(row["item-promotion-discount"] or "0.00"),
                float(row["shipping-price"] or "0.00"), float(row["ship-promotion-discount"] or "0.00"),
                float(row["gift-wrap-price"] or "0.00"),  # float(row["gift-promo-vat-excl-amount"]),
            ])
            total_tax_line_amount = sum([
                float(row["item-tax"] or "0.00"),  # float(row["item-promo-vat-amount"]),
                float(row["shipping-tax"] or "0.00"),  # float(row["shipping-promo-vat-amount"]),
                float(row["gift-wrap-tax"] or "0.00"),  # float(row["gift-promo-vat-amount"]),
            ])
            purchased_qty = int(row["quantity-shipped"])
            fulfillment_center = fc_env.search([
                ("code", "=", row["fulfillment-center-id"])
            ])
            if not fulfillment_center:
                _logger.info("No Fulfillment Center found for row %s" % row["fulfillment-center-id"])
                sync_log_env.create({
                    'account_id': self.account_id.id,
                    'operation_type': 'import_order',
                    'log_type': 'not_found',
                    'message': "No Fulfillment Center %s found for row %s" % (
                        row["fulfillment-center-id"] or row["amazon-order-item-id"]
                    ),
                    'user_id': self.env.user.id,
                    'amazon_order_ref': order_id,
                    'report_log_id': self.id,
                    "json_debug": str(row),
                })
                continue

            vals = {
                "amz_shipment_id": row["shipment-id"],
                "amz_shipment_date": shipment_date,
                # "item_promotion_id": row["item-promotion-id"],
                # "ship_promotion_id": row["ship-promotion-id"],
                "ship_from_address": row["carrier"],
                "fulfillment_center_id": fulfillment_center.id,
                "ship_from_country_id": fulfillment_center.country_id.id,
                "amz_total_net_line_amount": total_net_line_amount,
                "amz_total_tax_line_amount": total_tax_line_amount,
                "amz_transaction_inv_id": row["tracking-number"],
            }
            if not so_line.amazon_item_ref:
                vals["amazon_item_ref"] = row["amazon-order-item-id"]
            # Search for any additional SO lines
            additional_lines = sale_line_env.search([
                ("id", "!=", so_line.id),
                ("order_id.name", "=", order_id),
                ("amazon_item_ref", "like", row["amazon-order-item-id"]),
            ])
            if additional_lines:
                additional_lines.write({
                    "amz_shipment_id": vals["amz_shipment_id"],
                    "ship_from_country_id": vals["ship_from_country_id"],
                    "amz_transaction_inv_id": vals["amz_transaction_inv_id"],
                    "amz_transaction_refund_id": vals.get("amz_transaction_refund_id"),
                })

            if (
                so_line.ship_from_country_id and
                so_line.ship_from_country_id.id != vals["ship_from_country_id"]
            ):
                # Have to split the lines
                new_vals = vals.copy()
                new_vals.update({
                    "amazon_item_ref": "%s-%s" % (so_line.amazon_item_ref, vals["amz_shipment_id"]),
                    "price_unit": so_line.price_unit,
                    "product_uom_qty": purchased_qty,
                    "order_id": so_line.order_id.id,
                })
                so_line.write({
                    "price_unit": so_line.price_unit,
                    "product_uom_qty": (so_line.product_uom_qty -
                        int(new_vals["product_uom_qty"]))
                })
                new_so_line = so_line.copy(default=new_vals)
                new_so_line.with_context(
                    origin_country_id=vals["ship_from_country_id"])._compute_tax_id()
                so_lines |= new_so_line
                continue
            so_line.write(vals)
            # so_line.flush_recordset(["amz_shipment_id"])
            # so_line.with_context(
            #     origin_country_id=vals["ship_from_country_id"])._compute_tax_id()
            so_lines |= so_line
            """
            if row['is-business-order'] == 'true' and not so_line.order_id.is_amz_business_order:
                so_line.order_id.write({
                    "is_amz_business_order": True
                })
            if row["buyer-vat-number"] and not so_line.order_id.partner_invoice_id.vat:
                so_line.order_id.partner_invoice_id.write({
                    "vat": row["buyer-vat-number"]
                })
            """
        sale_orders = so_lines.mapped("order_id")
        self.write({
            "sale_order_ids": [(4, so_id) for so_id in sale_orders.ids],
        })
        self.env.cr.commit()

        draft_so = self.env["sale.order"]
        for so in self.sale_order_ids:
            # so.write({
            #     "need_to_push_pdf_invoice": True
            # })
            if so.amazon_channel != "fba":
                continue
            self.account_id._generate_stock_moves(so)
            if so.state == "draft":
                draft_so |= so
        draft_so.write({'state': 'done'})

        # self.env.cr.commit()
        wiz_env = self.env["sale.advance.payment.inv"]
        for so in self.sale_order_ids:
            lines_to_inv = so.order_line.filtered(lambda l: l.amz_transaction_inv_id and not l.invoice_lines)
            if not lines_to_inv:
                # Nothing to invoice
                continue
            try:
                so_inv = wiz_env.create({
                    "sale_order_ids": [(6, 0, [so.id])]
                })
                so_inv.create_invoices()
            except UserError as error:
                sync_log_env.create({
                    'account_id': self.account_id.id,
                    'operation_type': 'import_order',
                    'log_type': 'error',
                    'message': "Error when creating invoice for SO %s:\n%s" % (so, error),
                    'user_id': self.env.user.id,
                    'amazon_order_ref': so.name,
                    'report_log_id': self.id,
                    #"json_debug": str(row),
                })

        self.sale_order_ids.mapped("invoice_ids").filtered(
            lambda inv: inv.state == "draft").action_post()
        return True

    def process_report_GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA(self):
        imp_file = StringIO(base64.b64decode(self.report_file).decode())
        reader = csv.DictReader(imp_file, delimiter="\t")
        sale_env = self.env["sale.order"]
        sale_line_env = self.env["sale.order.line"]
        ticket_env = self.env["helpdesk.ticket"]
        sync_log_env = self.env["amazon.synchronization.log"]
        for row in reader:
            sale_order = sale_env.search([('amazon_order_ref', '=', row["order-id"])])
            return_date = fields.Date.from_string(row["return-date"])
            domain_search = [
                ("order_id", "=", sale_order.id),
                ("product_id.default_code", "=", row["sku"]),
                '|', ("fulfillment_center_id", "=", False),
                ("fulfillment_center_id.code", "=", row["fulfillment-center-id"]),
            ]
            so_line = sale_line_env.search(domain_search, order="id ASC", limit=1)
            if not so_line.move_ids:
                _logger.info("Order line %s is not shipped yet" % row)
                sync_log_env.create({
                    'account_id': self.account_id.id,
                    'operation_type': 'import_order',
                    'log_type': 'not_found',
                    'message': "Order line %s: %s is not shipped yet" % (row["order-id"], row["sku"]),
                    'user_id': self.env.user.id,
                    'amazon_order_ref': row["order-id"],
                    'report_log_id': self.id,
                    "json_debug": str(row),
                })
                continue
            if ticket_env.search([
                ("return_date", "=", return_date),
                ("sale_order_id", "=", sale_order.id),
                ("product_id.default_code", "=", row["sku"]),
                ("license_plate_number", "=", row["license-plate-number"]),
            ]):
                continue
            ticket_vals = {
                "name": "Amazon Return %s - %s: %s" % (row["order-id"], row["sku"], row["reason"]),
                "return_date": return_date,
                "return_reason": row["reason"],
                "customer_comment": row["customer-comments"],
                "returned_condition": row["detailed-disposition"],
                "amz_return_status": row["status"],
                "returned_to_fc": row["fulfillment-center-id"],
                "license_plate_number": row["license-plate-number"],
                "sale_order_id": sale_order.id,
                "partner_id": sale_order.partner_id.id,
                "partner_email": sale_order.partner_id.email,
                "product_id": so_line.product_id.id,
                "fba_return_report_id": self.id,
            }
            ticket = ticket_env.create(ticket_vals)
            return_wiz = self.env["stock.return.picking"].create({"ticket_id": ticket.id})
            return_wiz.create_returns()
        return True

    def fill_dictionary_from_file(self, reader):
        sync_log_env = self.env["amazon.synchronization.log"]
        amazon_product_env = self.env['amazon.offer']
        product_env = self.env['product.product']
        sellable_line_dict = {}
        unsellable_line_dict = {}
        for row in reader:
            seller_sku = row['sku']
            if not seller_sku:
                continue
            odoo_product = False
            amazon_product = amazon_product_env.search([
                ("asin", "=", row["asin"]),
                ("marketplace_id", "in", self.amz_marketplace_ids.ids),
                ("is_afn", "=", True),
            ], limit=1)
            if amazon_product:
                odoo_product = amazon_product.product_id
            else:
                odoo_product = product_env.search([('default_code', '=', row['sku'])], limit=1)
                if odoo_product:
                    amazon_product = amazon_product_env.search([
                        ("sku", "=", seller_sku),
                        ("marketplace_id", "in", self.amz_marketplace_ids.ids),
                        ("product_id", "=", odoo_product.id),
                    ], limit=1)
                    if amazon_product:
                        amazon_product.write({"asin": row["asin"]})
                    else:
                        amazon_product = amazon_product_env.create({
                            "account_id": self.account_id.id,
                            "asin": row["asin"],
                            "sku": seller_sku,
                            "marketplace_id": self.amz_marketplace_ids.id,
                            "product_id": odoo_product.id,
                            "is_afn": True,
                        })
            if not odoo_product:
                message = 'Amazon product not found for SKU %s or ASIN %s' % (seller_sku, row.get('asin'))
                sync_log_env.create({
                    'account_id': self.account_id.id,
                    'operation_type': 'import_order',
                    'log_type': 'not_found',
                    'message': message,
                    'user_id': self.env.user.id,
                    'report_log_id': self.id,
                    "json_debug": str(row),
                })
                continue

            sellable_line_dict[odoo_product] = float(row['afn-fulfillable-quantity'])
            unsellable_line_dict[odoo_product] = float(row['afn-unsellable-quantity'])

        return sellable_line_dict, unsellable_line_dict

    def process_fba_live_stock(self, line_dict, transit_loc, stock_loc):
        quant_env = self.env['stock.quant']
        move_vals = []
        quants = quant_env.search([
            ('location_id', '=', stock_loc.id),
            ('product_id', 'in', [p.id for p in line_dict.keys()]),
            ('is_outdated', '=', False),
        ])
        quants_to_adjust = self.env['stock.quant']
        for product, qty in line_dict.items():
            quant = quants.filtered(lambda q: q.product_id == product)
            if float_compare(quant.quantity, qty, precision_rounding=product.uom_id.rounding) == 0:
                continue
            if not quant and qty:
                quant = quant_env.create({
                    'product_id': product.id,
                    'location_id': stock_loc.id,
                    'inventory_quantity': qty,
                    'inventory_date': fields.Date.today(),
                })
            else:
                quant.write({"inventory_quantity": qty})
            quants_to_adjust |= quant

        for quant in quants_to_adjust:
            # Create and validate a move so that the quant matches its `inventory_quantity`.
            if float_compare(quant.inventory_diff_quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0:
                move_vals.append(
                    quant._get_inventory_move_values(
                        quant.inventory_diff_quantity,
                        transit_loc,
                        quant.location_id
                    )
                )
            else:
                move_vals.append(
                    quant._get_inventory_move_values(
                        -quant.inventory_diff_quantity,
                        quant.location_id,
                        transit_loc,
                        out=True
                    )
                )
        moves = self.env['stock.move'].with_context(inventory_mode=False).create(move_vals)
        moves._action_done()
        quants_to_adjust.location_id.write({'last_inventory_date': fields.Date.today()})
        date_by_location = {loc: loc._get_next_inventory_date() for loc in quants_to_adjust.mapped('location_id')}
        for quant in quants_to_adjust:
            quant.inventory_date = date_by_location[quant.location_id]
        quants_to_adjust.write({'inventory_quantity': 0, 'user_id': False})
        quants_to_adjust.write({'inventory_diff_quantity': 0})
        quants_to_adjust.inventory_quantity_set = False
        return moves.ids

    def process_report_GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA(self):
        self.ensure_one()
        imp_file = StringIO(base64.b64decode(self.report_file).decode())
        reader = csv.DictReader(imp_file, delimiter="\t")

        sellable_line_dict, unsellable_line_dict = self.fill_dictionary_from_file(reader)
        transit_location_id = self.amz_marketplace_ids[0].transit_location_id
        if not transit_location_id:
            raise UserError(_('Please define a Transit Location for Marketplace %s.') % (self.amz_marketplace_ids[0].name,))
        move_ids = []
        stock_loc = self.amz_marketplace_ids[0].fba_warehouse_id.lot_stock_id
        if not stock_loc:
            raise UserError(_('Please define a FBA warehouse for Marketplace %s.') % (self.amz_marketplace_ids[0].name,))

        unsellable_loc = self.amz_marketplace_ids[0].unsellable_location_id
        if unsellable_line_dict and not unsellable_loc:
            raise UserError(_('Please define a Unsellable Location for Marketplace %s.') % (self.amz_marketplace_ids[0].name,))

        move_ids += self.process_fba_live_stock(sellable_line_dict, transit_location_id, stock_loc)
        move_ids += self.process_fba_live_stock(unsellable_line_dict, transit_location_id, unsellable_loc)
        self.write({"fba_stock_move_ids": [(6, 0, move_ids)]})
        return True
