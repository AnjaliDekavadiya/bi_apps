# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MailActivitySchedule(models.TransientModel):

    _inherit = 'mail.activity.schedule'

    supervisor_user_id = fields.Many2one(
        'res.users',
        string='Supervisor',
        copy=False,
    )

    def _action_schedule_activities(self):
        res = super(MailActivitySchedule, self)._action_schedule_activities()
        if self.supervisor_user_id: 
            res['supervisor_user_id'] = self.supervisor_user_id.id
        return res