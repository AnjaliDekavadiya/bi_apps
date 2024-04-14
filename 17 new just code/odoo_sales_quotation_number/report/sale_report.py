# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    custom_number_quote = fields.Char(
        string='Quotation Number',
        readonly= True,
        copy=False,
    )

    # def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
    #     fields['custom_number_quote'] = ", s.custom_number_quote as custom_number_quote"
    #     groupby += ", s.custom_number_quote"
    #     return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['custom_number_quote'] = "s.custom_number_quote"
        return res
        
    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.custom_number_quote"""
        return res