# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    event_custom_id = fields.Many2one(
        'event.event', 
        readonly=True,
        string='Event'
    )

    @api.model
    def _select(self):
        return super(AccountInvoiceReport, self)._select()+ """,
            move.event_custom_id"""

