# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountReportFinance(models.TransientModel):
    _inherit = "accounting.report"

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string='Branch'
    )

#    @api.multi odoo13
    def check_report(self):
        res = super(AccountReportFinance, self).check_report()
        if self.company_branch_id:
            res['data']['form'].update({'company_branch_id': self.company_branch_id.id})
        return res

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
