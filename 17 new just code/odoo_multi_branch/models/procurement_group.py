# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    company_branch_id = fields.Many2one(
        'res.company.branch',
        string="Branch",
        copy=False,
        default=lambda self: self.env.user.company_branch_id.id,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
