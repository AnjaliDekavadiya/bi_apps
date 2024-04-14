# -*- coding: utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,api, models, tools


class ReportJobCostTrend(models.Model):

    _inherit = 'report.job.cost.volumn.trend'

    purchase_cost = fields.Float(
            string='Actual Purchased Cost',
            readonly=True
    )
    vendor_cost = fields.Float(
            string='Actual Vendor Bill Cost',
            readonly=True
    )
    timesheet_cost = fields.Float(
            string='Actual Timesheet Cost',
            readonly=True
    )

    job_cost_price = fields.Float(
        string=' Job Cost/Unit',
         readonly=True
    )

    def _select(self):
        return super(ReportJobCostTrend, self)._select() + ", jb.cost_price as job_cost_price, jb.actual_purchase_cost as purchase_cost, jb.actual_vendor_cost as vendor_cost,jb.actual_timesheet_cost as timesheet_cost"

    def _group_by(self):
        return super(ReportJobCostTrend, self)._group_by() + ",jb.cost_price ,jb.actual_purchase_cost,jb.actual_vendor_cost,jb.actual_timesheet_cost"