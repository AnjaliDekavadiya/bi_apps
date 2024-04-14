# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    sale_user_group_id = fields.Many2one(
        'sale.user.group',
        string='Sales Group',
    )

    def _select(self):
        return super()._select() + ", move.sale_user_group_id as sale_user_group_id"

    # def _select(self):
    #     return super(AccountInvoiceReport, self)._select() + ", move.sale_user_group_id as sale_user_group_id"
 
    # def _group_by(self):
    #     return super(AccountInvoiceReport, self)._group_by() + ", move.sale_user_group_id"

    # -------------------odoo13---------------------
    # def _select(self):
    #     select_st = super(AccountInvoiceReport, self)._select()
    #     select_st += ", sub.sale_user_group_id as sale_user_group_id"
    #     return select_st
        
    # def _sub_select(self):
    #     select_str = super(AccountInvoiceReport, self)._sub_select()
    #     select_str += ", ai.sale_user_group_id as sale_user_group_id"
    #     return select_str
    #------------------------------------------------

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
