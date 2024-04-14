# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import api, models, _


# Claim Report Class.
class srClaimReport(models.AbstractModel):
    _name = "report.sr_warranty_management.sr_claim_report_template"
    _description = "Claim Report Template"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["sr.claim.report.wizard"].browse(docids)
        claim_ids = False
        is_product_code = False
        is_product_number = False
        if docs:
            if docs and docs.state:
                claim_ids = self.env["sr.claim.warranty"].search(
                    [
                        ("date", ">=", docs.start_date),
                        ("date", "<=", docs.end_date),
                        ("state", "in", [docs.state]),
                    ]
                )
            else:
                claim_ids = self.env["sr.claim.warranty"].search(
                    [
                        ("date", ">=", docs.start_date),
                        ("date", "<=", docs.end_date),
                    ]
                )
            if claim_ids:
                for claim_id in claim_ids:
                    if claim_id and claim_id.product_ref_code:
                        is_product_code = True
                    if claim_id and claim_id.serial_number:
                        is_product_number = True
                return {
                    "claim_ids": claim_ids,
                    "docs": docs,
                    "is_product_code": is_product_code,
                    "is_product_number": is_product_number
                }
            else:
                return {
                    "docs": docs,
                    "is_product_code": is_product_code,
                    "is_product_number": is_product_number
                }
        else:
            return {
                "docs": docs,
                "is_product_code": is_product_code,
                "is_product_number": is_product_number
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: