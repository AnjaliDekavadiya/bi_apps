# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################
from odoo import api, fields, models, _
from datetime import date
import datetime
from datetime import datetime, timedelta
from functools import reduce
from markupsafe import Markup

# sr Product warranty class.


class srProductWarranty(models.Model):
    _name = "sr.product.warranty"
    _description = "Product Warranty"
    _rec_name = "name"
    _inherit = ["portal.mixin", "mail.thread",
                "mail.activity.mixin", "utm.mixin"]

    name = fields.Char("Name")
    company_id = fields.Many2one(
        "res.company",
        "Company",
    )

    # Customer Details
    partner_id = fields.Many2one("res.partner", "Customer")
    phone = fields.Char("Phone", related="partner_id.phone")
    email = fields.Char("Email", related="partner_id.email")

    # Product Details
    product_id = fields.Many2one("product.template", "Product")
    product_ref_code = fields.Char(
        "Product Code", related="product_id.default_code")
    product_barcode = fields.Char("Barcode", related="product_id.barcode")
    serial_number = fields.Char("Serial Number")
    qty = fields.Float("Quantity")

    # Warranty Details
    period = fields.Integer(
        "Warranty Period", related="product_id.period", store="True"
    )
    duration = fields.Selection(
        related="product_id.duration",
        store="True",
    )
    renewal_cost = fields.Float(
        "Renewal Cost", related="product_id.renew_cost", store="True"
    )
    is_allow_renew = fields.Boolean(
        "Allow Renew?", related="product_id.is_allow_renew")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    state = fields.Selection(
        [("in_warranty", "In Warranty"), ("expired_warranty", "Expired Warranty")],
        default="in_warranty",
    )
    warranty_date = fields.Date("Warranty Date")

    # Sale Details
    sale_order_id = fields.Many2one("sale.order", "Sale Order")
    sale_order_line_id = fields.Many2one("sale.order.line", "Sale Order Line")
    sale_order_count = fields.Integer(
        "Sale Order Count", compute="_get_sale_order")

    # Warranty history
    history_ids = fields.One2many("sr.history.warranty", "warranty_id")

    # Claim Details
    claim_ids = fields.Many2many(
        "sr.claim.warranty", "Claims", compute="_get_claim_records")
    claim_id = fields.Many2one("sr.claim.warranty", "Claim")
    claim_count = fields.Integer("Claim Count", compute="_get_claim")

    # Invoice details
    invoice_id = fields.Many2one("account.move", "Invoice")
    invoice_count = fields.Integer(
        string="Invoice Count", compute="_get_invoice")

    # Create function for create product warranty sequence.
    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code(
                    "sr.product.warranty") or "New"
            )
        result = super(srProductWarranty, self).create(vals)
        return result

    # Sale order count function.
    def _get_sale_order(self):
        self.sale_order_count = self.env["sale.order"].search_count(
            [("warranty_ids", "in", self.id), ('is_warranty', '=', True)]
        )

    # Open sale order view action function.
    def action_view_sale_order(self):
        return {
            "name": "Sale Order",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("warranty_ids", "in", self.id), ('is_warranty', '=', True)],
        }

    # Get claim records function
    def _get_claim_records(self):
        for rec in self:
            claim_ids = self.env["sr.claim.warranty"].search(
                [("warranty_id", "=", rec.id)]
            )
            if claim_ids:
                rec.claim_ids = claim_ids.ids
            else:
                rec.claim_ids = False

    # Claim count function.

    def _get_claim(self):
        self.claim_count = self.env["sr.claim.warranty"].search_count(
            [("warranty_id", "=", self.id)]
        )

    # Open claim warranty view action function.
    def open_view_claim_action(self):
        return {
            "name": "Claim",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "sr.claim.warranty",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("warranty_id", "=", self.id)],
        }

    # Invoice count function.
    def _get_invoice(self):
        self.invoice_count = self.env["account.move"].search_count(
            [("warranty_id", "=", self.id), ("move_type",
                                             "=", "out_invoice"), ('is_warranty', '=', True)]
        )

    # Open invoice view action function.
    def open_view_invoice_action(self):
        return {
            "name": "Invoice",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("warranty_id", "=", self.id), ("move_type", "=", "out_invoice"), ('is_warranty', '=', True)],
        }

    # Set warranty expired validity cron job function.
    def cron_warranty_expired_validity(self):
        warranty_ids = self.env["sr.product.warranty"].search(
            [("state", "in", ["in_warranty"])]
        )
        if warranty_ids:
            for warranty_id in warranty_ids:
                if warranty_id.end_date == date.today():
                    warranty_id.state = "expired_warranty"

    # Open renew warranty wizard action function
    def renew_warranty(self):
        action = self.env.ref("sr_warranty_management.sr_renew_warranty_action").read()[0]
        action["context"] = {"default_renew_cost": self.renewal_cost}
        return action

    # Claim warranty wizard action
    def claim_warranty(self):
        action = self.env.ref(
            "sr_warranty_management.sr_claim_warranty_wizard_action"
        ).read()[0]
        # action["context"] = {"default_renew_cost": self.renewal_cost}
        return action

    # Send mail data function.
    def send_mail_data(
        self,
        email_to,
        warranty_partner,
        product_list,
        start_date_list,
        end_date_list,
        warranty_list,
    ):

        msg = '<table style="border: 1px solid black;"><tbody><tr><th style="width:135px;border: 1px solid black; font-weight:bold; text-align:center;">Product</th><th style = "width: 135px;border: 1px solid black; font-weight:bold; text-align:center;"> Start Date </th><th style = "width: 135px;border: 1px solid black; font-weight:bold; text-align:center;"> End Date </th><th style = "width: 135px;border: 1px solid black; font-weight:bold; text-align:center;"> Warranty </th>'

        i = 0
        if product_list:
            for product in product_list:
                msg += (
                    '<tr><td style="border: 1px solid black; text-align:center;">'
                    + product
                    + " </td>"
                )
                msg += (
                    '<td style="border: 1px solid black; text-align:center;">'
                    + str(start_date_list[i])
                    + " </td>"
                )
                msg += (
                    '<td style="border: 1px solid black; text-align:center;">'
                    + str(end_date_list[i])
                    + " </td>"
                )
                msg += (
                    '<td style="border: 1px solid black; text-align:center;">'
                    + warranty_list[i]
                    + " </td></tr>"
                )
                i += 1
        msg += "</tbody></table/>"
        output = msg
        if output:
            self.send_mail(email_to, warranty_partner, output)

    # Send mail multiple data function.
    def send_mail_mul_data(
        self,
        email_to,
        warranty_partner,
        mul_product_list,
        mul_start_date_list,
        mul_end_date_list,
        mul_warranty_list,
    ):

        msg = '<table style="border: 1px solid black;"><tbody><tr><th style="width:135px;border: 1px solid black; font-weight:bold; text-align:center;">Product</th><th style = "width: 135px;border: 1px solid black; font-weight:bold; text-align:center;"> Start Date </th><th style = "width: 135px;border: 1px solid black; font-weight:bold; text-align:center;"> End Date </th><th style = "width: 135px;border: 1px solid black; font-weight:bold; text-align:center;"> Warranty </th>'

        i = 0
        if mul_product_list:
            for product in mul_product_list:
                msg += (
                    '<tr><td style="border: 1px solid black; text-align:center;">'
                    + product
                    + " </td>"
                )
                msg += (
                    '<td style="border: 1px solid black; text-align:center;">'
                    + str(mul_start_date_list[i])
                    + " </td>"
                )
                msg += (
                    '<td style="border: 1px solid black; text-align:center;">'
                    + str(mul_end_date_list[i])
                    + " </td>"
                )
                msg += (
                    '<td style="border: 1px solid black; text-align:center;">'
                    + mul_warranty_list[i]
                    + " </td></tr>"
                )
                i += 1

        msg += "</tbody></table/>"
        output = msg
        if output:
            self.send_mail(email_to, warranty_partner, output)

    # Send mail function.
    def send_mail(self, email_to, warranty_partner, output):
        mail = {}
        if email_to and output:
            mail_subject = "Warranty Expire Notification"
            mail_body = """<font size=""2""> <p> Hello {0} </p><p>Your product warranty will be expire in below date </p> <p> {1} </p> <p> Kind Regards,</p> <p> {2} </p> </font>""".format(
                warranty_partner, output, self.env.user.name
            )
            mail = {
                "subject": mail_subject,
                "email_from": self.env.user.name,
                "recipient_ids": [(6, 0, email_to)],
                "body_html": mail_body,
                # "body_html": "<p> Test </p>",
            }
            if mail:
                mail_id = self.env["mail.mail"].create(mail)
                if mail_id:
                    mail_id.send()

    # Get data of wararnty expire notification function.
    def cron_warranty_expire_notification(self):
        warranty_partner = False
        email_to = []

        company_id = self.env["res.company"].search(
            [("id", "=", self.env.user.company_id.id)]
        )
        if company_id and company_id.period:
            warranty_ids = self.env["sr.product.warranty"].search(
                [("state", "in", ["in_warranty"]),
                 ("company_id", "=", company_id.id)]
            )
            if warranty_ids:
                for partner_id in warranty_ids.mapped("partner_id"):
                    partner_warr_ids = warranty_ids.filtered(
                        lambda x: x.partner_id == partner_id
                    )
                    date_list = reduce(
                        lambda re, x: re + [x] if x not in re else re,
                        partner_warr_ids.mapped("end_date"),
                        [],
                    )
                    for date in date_list:
                        date_partner_warr_ids = partner_warr_ids.filtered(
                            lambda x: x.end_date == date
                        )
                        if len(date_partner_warr_ids) > 1:
                            mul_product_list = []
                            mul_start_date_list = []
                            mul_end_date_list = []
                            mul_warranty_list = []
                            for warranty_id in date_partner_warr_ids:
                                less_than_date = warranty_id.end_date - timedelta(
                                    days=company_id.period
                                )
                                if less_than_date == date.today():
                                    mul_product_list.append(
                                        warranty_id.product_id.name)
                                    mul_start_date_list.append(
                                        warranty_id.start_date)
                                    mul_end_date_list.append(
                                        warranty_id.end_date)
                                    mul_warranty_list.append(warranty_id.name)
                                    email_to = [warranty_id.partner_id.id]
                                    warranty_partner = warranty_id.partner_id.name
                            if (
                                mul_product_list
                                and mul_start_date_list
                                and mul_end_date_list
                                and mul_warranty_list
                            ):
                                self.send_mail_mul_data(
                                    email_to,
                                    warranty_partner,
                                    mul_product_list,
                                    mul_start_date_list,
                                    mul_end_date_list,
                                    mul_warranty_list,
                                )
                        else:
                            product_list = []
                            start_date_list = []
                            end_date_list = []
                            warranty_list = []
                            for warranty_id in date_partner_warr_ids:
                                less_than_date = warranty_id.end_date - timedelta(
                                    days=company_id.period
                                )
                                if less_than_date == date.today():
                                    product_list.append(
                                        warranty_id.product_id.name)
                                    start_date_list.append(
                                        warranty_id.start_date)
                                    end_date_list.append(warranty_id.end_date)
                                    warranty_list.append(warranty_id.name)
                                    email_to = [warranty_id.partner_id.id]
                                    warranty_partner = warranty_id.partner_id.name
                                    self.send_mail_data(
                                        email_to,
                                        warranty_partner,
                                        product_list,
                                        start_date_list,
                                        end_date_list,
                                        warranty_list,
                                    )


# sr History warranty class.
class srHistoryWarranty(models.Model):
    _name = "sr.history.warranty"
    _description = "History Warranty"

    warranty_id = fields.Many2one("sr.product.warranty")
    partner_id = fields.Many2one("res.partner", "Customer")
    product_id = fields.Many2one("product.template", "Product")
    serial_number = fields.Char("Serial Number")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    renewal_cost = fields.Float("Renewal Cost")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: