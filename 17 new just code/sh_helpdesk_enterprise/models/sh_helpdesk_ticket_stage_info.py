# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class ShHelpdeskTeamInfo(models.Model):
    _name="sh.helpdesk.ticket.stage.info"
    _description="Helpdesk Task Information"

    stage_task_id = fields.Many2one("helpdesk.ticket",string="Stage task")
    stage_name=fields.Char(string="Stage Name")
    date_in=fields.Datetime(string="Date In")
    date_in_by=fields.Many2one("res.users",string="Date In By")
    date_out=fields.Datetime(string="Date Out")
    date_out_by=fields.Many2one("res.users",string="Date Out By")
    day_diff=fields.Integer(string="Day Diff")
    time_diff=fields.Float(string="Time Diff")
    total_time_diff=fields.Float(string="Total Time Diff")
