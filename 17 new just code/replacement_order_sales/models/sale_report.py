# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    replacement_reason_custom_id = fields.Many2one(
        'replacement.reason.custom',
        string='Repalcement Reason',
        readonly=True,
        store=True,
    )
    replacement_custoriginal_salesorder_id = fields.Many2one(
        'sale.order',
        string='Original Sale Order',
        readonly=True,
        store=True,
    )

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['replacement_reason_custom_id','replacement_custoriginal_salesorder_id'] = ", s.replacement_reason_custom_id as replacement_reason_custom_id, s.replacement_custoriginal_salesorder_id as replacement_custoriginal_salesorder_id"
        groupby += ", s.replacement_reason_custom_id, s.replacement_custoriginal_salesorder_id"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
        