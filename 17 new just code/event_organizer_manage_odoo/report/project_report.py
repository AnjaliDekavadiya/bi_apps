# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    event_custom_id = fields.Many2one(
        'event.event', 
        readonly=True,
        string='Event'
    )

    @api.model
    def _select(self):
        return super(ReportProjectTaskUser, self)._select()+ """,
            t.event_custom_id"""

    def _group_by(self):
        return super(ReportProjectTaskUser, self)._group_by()+ """,
            t.event_custom_id"""
