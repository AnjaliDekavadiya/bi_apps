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
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

# Inherited sale order class.


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Warranty detail fields
    warranty_ids = fields.Many2many(comodel_name="sr.product.warranty")
    warranty_count = fields.Integer(
        string="Warranty Count", compute="_get_warranty")
    is_warranty = fields.Boolean("#is Warranty")

    # Claim detail fields
    claim_id = fields.Many2one("sr.claim.warranty")
    claim_count = fields.Integer("Claim Count", compute="_get_claim")

    # Override the copy_data(Duplicate) function.
    def copy_data(self, default=None):
        result = super().copy_data(default)
        if "warranty_ids" in result[0] and result[0]["warranty_ids"]:
            result[0]["warranty_ids"] = []
        if "order_line" in result[0] and result[0]["order_line"]:
            for line in result[0]["order_line"]:
                if "warranty_id" in line[2]:
                    line[2]["warranty_id"] = False
        return result

    # Warranty count function
    def _get_warranty(self):
        self.warranty_count = self.env["sr.product.warranty"].search_count(
            [("sale_order_id", "=", self.id)]
        )

    # Open warranty view action function
    def action_view_warranty(self):
        action = self.env.ref(
            "sr_warranty_management.sr_product_warranty_action"
        ).read()[0]
        action["views"] = [
            (
                self.env.ref(
                    "sr_warranty_management.sr_product_warranty_tree_view").id,
                "tree",
            ),
            (
                self.env.ref(
                    "sr_warranty_management.sr_product_warranty_form_view").id,
                "form",
            ),
        ]
        action["domain"] = [("sale_order_id", "=", self.id)]
        return action

    # Claim count function
    def _get_claim(self):
        self.claim_count = self.env["sr.claim.warranty"].search_count(
            [("sale_order_id", "=", self.id)]
        )

    # Open claim view action function
    def action_view_claim_warranty(self):
        return {
            "name": "Claim Warranty",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "sr.claim.warranty",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("sale_order_id", "=", self.id)],
        }

    # Create warranty records function.
    def create_warranty_records(self, sale_id):
        warranty_details = {}
        warranty_list = []
        warranty_obj = self.env["sr.product.warranty"]
        if sale_id and sale_id.order_line:
            for line in sale_id.order_line:
                if line.product_id and line.product_id.is_warranty:
                    start_date = line.order_id.date_order
                    if line.product_id.duration == "days":
                        date_obj = start_date + datetime.timedelta(
                            days=line.product_id.period
                        )
                    elif line.product_id.duration == "months":
                        date_obj = start_date + relativedelta(
                            months=+line.product_id.period
                        )
                    elif line.product_id.duration == "years":
                        date_obj = start_date + relativedelta(
                            years=+line.product_id.period
                        )
                    else:
                        date_obj = False
                    if date_obj:
                        start_date = start_date
                        end_date = date_obj
                    else:
                        start_date = False
                        end_date = False
                    warranty_details = {
                        "partner_id": line.order_id.partner_id.id,
                        "product_id": line.product_id.product_tmpl_id.id,
                        "start_date": start_date,
                        "end_date": end_date,
                        "company_id": sale_id.company_id.id,
                        "qty": line.product_uom_qty,
                        "warranty_date": date.today(),
                    }
                    warranty_id = warranty_obj.sudo().create(warranty_details)
                    if warranty_id:
                        warranty_list.append(warranty_id.id)
                        line.warranty_id = warranty_id.id
                        line.order_id.warranty_ids = warranty_list
                        warranty_id.sale_order_id = line.order_id.id
                        warranty_id.sale_order_line_id = line.id


# inherited sale order line class.
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warranty_id = fields.Many2one("sr.product.warranty")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: