# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    timesheet_to_approve_count = fields.Integer(
        compute='_compute_timesheet_to_approve', string='Timesheet to Approve')

    def _compute_timesheet_to_approve(self):
        timesheet_data = self.env['hr_timesheet_sheet.sheet'].read_group(
            [('department_id', 'in', self.ids), ('state', '=', 'confirm')], ['department_id'], ['department_id'])
        result = dict((data['department_id'][0], data['department_id_count']) for data in timesheet_data)
        for department in self:
            department.timesheet_to_approve_count = result.get(department.id, 0)
