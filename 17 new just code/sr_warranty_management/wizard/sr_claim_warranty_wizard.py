# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import fields, models, _
from datetime import date

# sr Claim Warranty Wizard class.


class srClaimWarrantyWizard(models.TransientModel):
    _name = "sr.claim.warranty.wizard"
    _description = "Claim Warranty"

    issue = fields.Text("Issue Description")

    # Create claim warranty details function
    def create_claim_warranty(self):
        active_id = self.env["sr.product.warranty"].browse(
            self.env.context.get("active_id")
        )
        if active_id:
            claim_id = (
                self.env["sr.claim.warranty"]
                .sudo()
                .create(
                    {
                        "issue": self.issue,
                        "date": date.today(),
                        "warranty_id": active_id.id,
                        "partner_id": active_id.partner_id.id,
                        "product_id": active_id.product_id.id,
                        "serial_number": active_id.serial_number,
                        "start_date": active_id.start_date,
                        "end_date": active_id.end_date,
                        "warranty_state": active_id.state,
                        "warranty_sale_order_id": active_id.sale_order_id.id,
                        "state": "review",
                    }
                )
            )
            if claim_id:
                active_id.claim_id = claim_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: