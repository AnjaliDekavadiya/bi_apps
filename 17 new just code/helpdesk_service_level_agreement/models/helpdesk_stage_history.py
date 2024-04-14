# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class HelpdeskStageHistory(models.Model):
    _name = 'helpdesk.stage.history'
    _description = 'Helpdesk Stage History'

#    @api.multi odoo13
    @api.depends(
        'overtime_hours',
        'working_time'
    )
    def _compute_consumed_time(self):
        for rec in self:
            rec.consumed_time = rec.overtime_hours + rec.working_time

    @api.depends(
        'consumed_time',
        'estimate_time'
    )
    def _compute_delay_time(self):
        for line in self:
            line.delay_time = 0.0
            if line.consumed_time > 0.0 and line.estimate_time > 0.0:
                line.delay_time = line.consumed_time - line.estimate_time

    @api.depends(
        'start_time',
        'end_time'
    )
    def _compute_working_time(self):
        for line in self:
#            odoo13
            line.working_time = 0.0
            if line.start_time and line.end_time:
                start_time = datetime.strptime(str(line.start_time), '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(str(line.end_time), '%Y-%m-%d %H:%M:%S')
                if line.calendar_id:
                    consumed_hours = line.calendar_id.get_work_hours_count(
                        start_time,
                        end_time,
                        compute_leaves=True)
#                        compute_leaves=True, resource_id=False)
                    line.working_time = consumed_hours


    helpdesk_ticket_id = fields.Many2one(
        'helpdesk.support',
        string="Support Ticket",
    )
    stage_id = fields.Many2one(
        'helpdesk.stage.config',
        string="Source Stage",
        required=False,
    )
    dest_stage_id = fields.Many2one(
        'helpdesk.stage.config',
        string="Stage",
        required=False,
    )
    start_time = fields.Datetime(
        string="Start At",
    )
    end_time = fields.Datetime(
        string="Done At",
    )
    estimate_time = fields.Float(
        string="Estimated Time(HH:MM)",
    )
    consumed_time = fields.Float(
        string="Consumed Time(HH:MM)",
        compute="_compute_consumed_time",
        store=True,
    )
    overtime_hours = fields.Float(
        string="Overtime Hours(HH:MM)",
    )
    delay_time = fields.Float(
        string="Delay(HH:MM)",
        compute="_compute_delay_time",
        store=True,
    )
    working_time = fields.Float(
        string="Working Hours(HH:MM)",
        compute="_compute_working_time",
        store=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string="Responsible User",
    )
    team_id = fields.Many2one(
        'support.team',
        string="Team",
    )
    calendar_id = fields.Many2one(
        'resource.calendar',
        'Resource Calendar',
        required=False,
    )
