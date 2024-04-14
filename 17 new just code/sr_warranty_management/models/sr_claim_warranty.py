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
from odoo.exceptions import ValidationError


# sr Claim warranty class.
class srClaimWarranty(models.Model):
    _name = "sr.claim.warranty"
    _description = "Claim Warranty"
    _rec_name = "name"
    _inherit = ["portal.mixin", "mail.thread",
                "mail.activity.mixin", "utm.mixin"]

    name = fields.Char("Name")

    # Claim Details
    issue = fields.Text("Issue Description")
    date = fields.Date("Claim Date")
    state = fields.Selection(
        [
            ("review", "Review"),
            ("repair", "Repair"),
            ("done", "Done"),
            ("reject", "Reject"),
        ],
        string="Claim Status",
    )
    reason = fields.Text("Refuse Reason")
    claim_warranty_parts_ids = fields.One2many(
        "sr.claim.warranty.parts", "claim_warranty_id"
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

    # Warranty Details
    warranty_id = fields.Many2one("sr.product.warranty")
    start_date = fields.Date("Warranty Start Date")
    end_date = fields.Date("Warranty End Date")
    warranty_state = fields.Selection(
        [("in_warranty", "In Warranty"), ("expired_warranty", "Expired Warranty")],
        string="Warranty Status",
    )
    warranty_count = fields.Integer("Warranty Count", compute="_get_warranty")
    warranty_sale_order_id = fields.Many2one(
        "sale.order", "Warranty Sale Order")

    # Sale Details
    sale_order_id = fields.Many2one("sale.order", "Claim Sale Order")
    sale_order_count = fields.Integer(
        "Sale Order Count", compute="_get_claim_sale_order"
    )
    is_order = fields.Boolean("Is Order?")

    # Create function for create claim warranty sequence.
    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code(
                    "sr.claim.warranty") or "New"
            )
        result = super(srClaimWarranty, self).create(vals)
        return result

    # Get warranty count function.
    def _get_warranty(self):
        self.warranty_count = self.env["sr.product.warranty"].search_count(
            [("claim_id", "=", self.id)]
        )

    # Open warranty view action.
    def open_view_warranty_action(self):
        return {
            "name": "Warranty",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "sr.product.warranty",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("claim_id", "=", self.id)],
        }

    # Claim accept function.
    def claim_accept(self):
        self.state = "repair"
        self.is_order = True

    # Claim done function.
    def claim_done(self):
        self.state = "done"

    # Claim refuse function.
    def claim_refuse(self):
        action = self.env.ref(
            "sr_warranty_management.sr_claim_refuse_reason_action"
        ).read()[0]
        return action

    # Claim parts sale order function.
    def claim_parts_sale_order(self):
        order_list = []
        if not self.claim_warranty_parts_ids:
            raise ValidationError(_("Please insert the Parts details."))
        if self.claim_warranty_parts_ids:
            for line in self.claim_warranty_parts_ids:
                order_list.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id.product_variant_id.id,
                            "product_uom_qty": line.qty,
                        },
                    )
                )
            sale_order_id = self.env["sale.order"].create(
                {
                    "partner_id": self.partner_id.id,
                    "claim_id": self.id,
                    "order_line": order_list,
                    "is_warranty": True,
                }
            )
            if sale_order_id:
                self.sale_order_id = sale_order_id.id
                self.state = "done"
                self.is_order = False

    # Sale order count function.
    def _get_claim_sale_order(self):
        self.sale_order_count = self.env["sale.order"].search_count(
            [("claim_id", "=", self.id), ('is_warranty', '=', True)]
        )

    # Open sale order view action function.
    def action_view_calim_sale_order(self):
        return {
            "name": "Sale Order",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "sale.order",
            "views": [(False, "tree"), (False, "form")],
            "domain": [("claim_id", "=", self.id), ('is_warranty', '=', True)],
        }


# sr Claim warranty parts class.
class srClaimWarrantyParts(models.Model):
    _name = "sr.claim.warranty.parts"
    _description = "Claim Warranty Parts"

    claim_warranty_id = fields.Many2one("sr.claim.warranty")
    product_id = fields.Many2one("product.template", "Product")
    qty = fields.Float("Quantity", default=1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: