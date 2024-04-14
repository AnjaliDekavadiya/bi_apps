# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class DisqualifyReason(models.Model):
    _name = 'disqualify.reason'
    _description = "Disqualify Reason"

    name = fields.Html(string="Disqualify Reason")
    allow_resubmit = fields.Boolean(string="Allow Resubmit")

    def action_dis_qualify(self):
        rec = self._context.get('active_id')
        bid = self.env['tender.bidding'].browse(rec)
        if bid.bid_document_ids:
            for data in bid.bid_document_ids:
                data.unlink()
            bid.write({
                'dis_qualified_reason': self.name,
                'responsible_id': self.env.user.id,
                'allow_resubmit': self.allow_resubmit
            })
            bid.action_disqualified_bid()
            mail_template = self.env.ref('tk_tender_management.disqualified_vendor_mail_template')
            if mail_template:
                mail_template.send_mail(bid.id, force_send=True)
        else:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'info',
                    'title': 'Attach documents for Qualified or Disqualify Vendor',
                    'sticky': False,
                }
            }
            return message
