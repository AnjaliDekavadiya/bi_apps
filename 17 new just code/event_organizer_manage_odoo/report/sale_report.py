# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleReport(models.Model):
    _inherit = "sale.report"

    event_custom_id = fields.Many2one(
        'event.event', 
        readonly=True,
        string='Event'
    )

    # def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
    #     fields['event_custom_id'] = ", s.event_custom_id as event_custom_id"
    #     groupby += ', s.event_custom_id'
    #     return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['event_custom_id'] = "s.event_custom_id"
        return res
        
    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.event_custom_id"""
        return res