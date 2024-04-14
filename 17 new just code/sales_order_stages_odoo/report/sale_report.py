# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
 
class SaleReport(models.Model):
    _inherit = 'sale.report'
    
    custom_stage_id = fields.Many2one(
        'custom.sale.order.stage',
        string="Stage",
        readonly=True
    )

    # def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
    #     fields['custom_stage_id'] = ", s.custom_stage_id as custom_stage_id"
    #     groupby += ", s.custom_stage_id"
    #     return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause) 

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['custom_stage_id'] = "s.custom_stage_id"
        return res

    
    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.custom_stage_id"""
        return res        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: