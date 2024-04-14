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


# sr Claim refuse reason class.
class srClaimRefuseReason(models.TransientModel):
    _name = "sr.claim.refuse.reason"
    _description = "Claim Refuse Reason"

    reason = fields.Text("Refuse Reason")

    # Update refuse reason details function
    def update_refuse_reason(self):
        active_id = self.env["sr.claim.warranty"].browse(
            self.env.context.get("active_id")
        )
        if active_id:
            active_id.reason = self.reason
            active_id.state = "reject"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: