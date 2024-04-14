# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleEstimate(models.Model):
    _inherit = "sale.estimate"

    event_custom_id = fields.Many2one(
        'event.event',
        string='Event',
        copy=False,
    )

    def estimate_to_quotation(self):
        res = super(SaleEstimate, self).estimate_to_quotation()
        self.quotation_id.write({
            'event_custom_id':self.event_custom_id.id,
            })
        return res
