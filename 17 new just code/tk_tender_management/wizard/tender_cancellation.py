# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class TenderCancellation(models.TransientModel):
    _name = "tender.cancel"
    _description = "Tender Cancellation"

    name = fields.Html(string="Cancellation Reason")

    def action_cancel_tender(self):
        active_id = self._context.get('active_id')
        tender_id = self.env['tender.information'].browse(active_id)
        tender_id.write({
            'cancellation_reason': self.name,
            'stage': 'cancel'
        })
        if tender_id.tender_bid_ids:
            for rec in tender_id.tender_bid_ids:
                if rec.qualify_status == "qualified":
                    rec.stage = "lost"
                    mail_template = self.env.ref('tk_tender_management.tender_cancellation_mail_template')
                    if mail_template:
                        mail_template.send_mail(rec.id, force_send=True)
