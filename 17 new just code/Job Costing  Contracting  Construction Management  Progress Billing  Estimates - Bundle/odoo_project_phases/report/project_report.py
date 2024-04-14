# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    project_phase_id = fields.Many2one(
        'project.phase',
        string='Project Phase',
    )

    # def _select(self):
    #     select_str = super(ReportProjectTaskUser, self)._select()
    #     select_str += ", t.project_phase_id as project_phase_id"
    #     return select_str

    # def _group_by(self):
    #     group_by_str = super(ReportProjectTaskUser, self)._group_by()
    #     group_by_str += ", t.project_phase_id"
    #     return group_by_str

    @api.model
    def _select(self):
        return super(ReportProjectTaskUser, self)._select()+ """,
            t.project_phase_id"""

    def _group_by(self):
        return super(ReportProjectTaskUser, self)._group_by()+ """,
            t.project_phase_id"""

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
