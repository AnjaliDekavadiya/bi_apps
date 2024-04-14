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


# Warranty Report Class.
class srWarrantyReport(models.AbstractModel):
    _name = "report.sr_warranty_management.sr_warranty_report_template"
    _description = "Warranty Report Template"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["sr.warranty.report.wizard"].browse(docids)
        warranty_ids = False
        is_product_number = False
        is_product_code = False
        if docs:
            if docs and docs.state:
                warranty_ids = self.env["sr.product.warranty"].search(
                    [
                        ("warranty_date", ">=", docs.start_date),
                        ("warranty_date", "<=", docs.end_date),
                        ("state", "in", [docs.state]),
                    ]
                )
            else:
                warranty_ids = self.env["sr.product.warranty"].search(
                    [
                        ("warranty_date", ">=", docs.start_date),
                        ("warranty_date", "<=", docs.end_date),
                    ]
                )
            if warranty_ids:
                for warranty_id in warranty_ids:
                    if warranty_id and warranty_id.serial_number:
                        is_product_number = True
                    if warranty_id and warranty_id.product_ref_code:
                        is_product_code = True
                return {
                    "warranty_ids": warranty_ids,
                    "docs": docs,
                    "is_product_number": is_product_number,
                    "is_product_code": is_product_code,
                }
            else:
                return {
                    "docs": docs,
                    "is_product_number": is_product_number,
                    "is_product_code": is_product_code,
                }
        else:
            return {
                "docs": docs,
                "is_product_number": is_product_number,
                "is_product_code": is_product_code,
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: