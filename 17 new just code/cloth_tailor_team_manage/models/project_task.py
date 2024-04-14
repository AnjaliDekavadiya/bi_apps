# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID

class ProjectTask(models.Model):
    _inherit = 'project.task'

    tailor_team_id = fields.Many2one(
        'tailor.team',
        related = 'cloth_request_id.tailor_team_id',
        string="Team",
        store=True
    )

    # @api.model
    # def create(self, vals):
    #     if vals.get('cloth_request_id'):
    #         cloth_request_id = self.env['cloth.request.details'].browse(vals.get('cloth_request_id'))
    #         if cloth_request_id.tailor_team_id:
    #             vals.update({
    #                 'tailor_team_id': cloth_request_id.tailor_team_id.id
    #             })
    #     return super(ProjectTask, self).create(vals)