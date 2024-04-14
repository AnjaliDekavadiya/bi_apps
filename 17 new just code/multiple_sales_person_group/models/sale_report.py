# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleReport(models.Model):
    _inherit = "sale.report"
    
    sale_user_group_id = fields.Many2one(
        'sale.user.group',
        string='Sales Group',
    )

    # odoo11
    # def _select(self):
    #     select_str = super(SaleReport, self)._select()
    #     select_str += ", s.sale_user_group_id as sale_user_group_id"
    #     return select_str

    # def _group_by(self):
    #     group_by_str = super(SaleReport, self)._group_by()
    #     group_by_str += ", s.sale_user_group_id"
    #     return group_by_str

    # odoo12
    # def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
    #     fields['sale_user_group_id'] = ", s.sale_user_group_id as sale_user_group_id"
    #     groupby += ", s.sale_user_group_id"
    #     return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['sale_user_group_id'] = "s.sale_user_group_id"
        return res
        
    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.sale_user_group_id"""
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
