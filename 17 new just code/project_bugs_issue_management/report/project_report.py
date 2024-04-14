# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools
import logging
_logger = logging.getLogger(__name__)



class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    custom_type = fields.Selection([
        ('task', 'Task'),
        ('bugs_issues', 'Bugs & Issues'),
        ], 
        string='Type', 
        default='task',
    )

    def _select(self):
        res = super(ReportProjectTaskUser, self)._select()
        res += ', t.custom_type'
        return res

    def _group_by(self):
        res = super(ReportProjectTaskUser, self)._group_by()
        res += ', t.custom_type'
        return res