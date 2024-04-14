# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    custom_purchase_requisition_limit = fields.Float(
        string='Requisition Limit Per Requisition', 
        copy=False,
        groups='hr.group_hr_user',
    )
    custom_monthly_purchase_requisition_limit = fields.Float(
        string='Monthly Requisition Limit', 
        copy=False,
        groups='hr.group_hr_user',
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
