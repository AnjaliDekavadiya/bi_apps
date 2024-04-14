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
import datetime
from dateutil.relativedelta import relativedelta

# sr Renew Warranty class.


class srRenewWarranty(models.TransientModel):
    _name = "sr.renew.warranty"
    _description = "Renew Warranty"

    period = fields.Integer("Warranty Period")
    duration = fields.Selection(
        [("days", "Days"), ("months", "Months"), ("years", "Years")], default="days"
    )
    renew_cost = fields.Float("Renew Cost")

    # Update renew warranty details function
    def update_renew_warranty(self):
        invoice_obj = self.env['account.move']
        if self.period and self.period > 0:
            active_id = self.env["sr.product.warranty"].browse(
                self.env.context.get("active_id")
            )
            if active_id:
                active_id.sudo().write(
                    {
                        "history_ids": [
                            (
                                0,
                                0,
                                {
                                    "warranty_id": active_id.id,
                                    "partner_id": active_id.partner_id.id,
                                    "product_id": active_id.product_id.id,
                                    "serial_number": active_id.serial_number,
                                    "start_date": active_id.start_date,
                                    "end_date": active_id.end_date,
                                    "renewal_cost": active_id.renewal_cost,
                                },
                            )
                        ]
                    }
                )
                start_date = active_id.end_date
                if self.duration == "days":
                    date_obj = start_date + \
                        datetime.timedelta(days=self.period)
                elif self.duration == "months":
                    date_obj = start_date + relativedelta(months=+self.period)
                elif self.duration == "years":
                    date_obj = start_date + relativedelta(years=+self.period)
                else:
                    date_obj = False
                if date_obj:
                    start_date = start_date
                    end_date = date_obj
                else:
                    start_date = False
                    end_date = False
                active_id.write(
                    {
                        "start_date": start_date,
                        "end_date": end_date,
                        "period": self.period,
                        "duration": self.duration,
                        "renewal_cost": self.renew_cost,
                        "state": "in_warranty",
                    }
                )
                if active_id.product_id.product_variant_id:
                    product = active_id.product_id.product_variant_id
                    account_id = False
                    if product.id:
                        account_id = product.property_account_income_id
                    if not account_id:
                        account_id = product.categ_id.property_account_income_categ_id
                    invoice_id = invoice_obj.create({
                        "warranty_id": active_id.id,
                        "partner_id": active_id.partner_id.id,
                        "move_type": "out_invoice",
                        "is_warranty": True,
                        "invoice_line_ids": [(0, 0, {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": self.renew_cost,
                            "account_id": account_id.id,
                        })]
                    })
                    if invoice_id:
                        active_id.invoice_id = invoice_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: