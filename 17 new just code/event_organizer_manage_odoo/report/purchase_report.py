# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    event_custom_id = fields.Many2one(
        'event.event', 
        readonly=True,
        string='Event'
    )
  
    def _select(self):
        return super(PurchaseReport, self)._select()+ """,
            po.event_custom_id"""