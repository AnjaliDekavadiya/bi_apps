# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _
from textwrap import shorten
from odoo.tools import format_date


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def sh_rr_get_printed_report_name(self, show_ref=False):
        self.ensure_one()
        name = ""
        if self.state == "draft":
            name += {
                "out_invoice": _("Draft Invoice"),
                "out_refund": _("Draft Credit Note"),
                "in_invoice": _("Draft Bill"),
                "in_refund": _("Draft Vendor Credit Note"),
                "out_receipt": _("Draft Sales Receipt"),
                "in_receipt": _("Draft Purchase Receipt"),
                "entry": _("Draft Entry"),
            }[self.move_type]
            name += " "
        if not self.name or self.name == "/":
            name += "(* %s)" % str(self.id)
        else:
            name += self.name
            if self.env.context.get("input_full_display_name"):
                if self.partner_id:
                    name += f", {self.partner_id.name}"
                if self.date:
                    name += f", {format_date(self.env, self.date)}"
        return name + (
            f" ({shorten(self.ref, width=50)})" if show_ref and self.ref else ""
        )
