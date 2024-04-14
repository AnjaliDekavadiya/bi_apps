# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        readonly=True
    )

    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.company_branch_id as company_branch_id"


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
