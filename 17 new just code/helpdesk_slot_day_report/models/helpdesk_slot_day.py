# -*- coding: utf-8 -*-

from odoo import models, fields,api
from datetime import datetime
from datetime import date, timedelta
import time
import pytz


class HelpdeskSlot(models.Model):
    _name = 'helpdesk.slot'
    _description = 'Helpdesk Slot Configuration'

    name = fields.Char(
        string="Name",
        required=True,
    )
    start_time = fields.Float(
        string="Start Time",
        required=True,
    )
    end_time = fields.Float(
        string="End Time",
        required=True,
    )

class HelpdeskStageHistory(models.Model):
    _inherit = 'helpdesk.stage.history'
    _description = 'Helpdesk Stage History'

    def _convert_to_realtime(self, localdatetime=None):
        check_in_date = localdatetime
        timezone_tz = 'utc'
        user_id = self.env.user
        if user_id and user_id.tz:
            timezone_tz = user_id.tz
            local = pytz.timezone(timezone_tz)
            local_dt = local.utcoffset(check_in_date)
        else:
            timezone_tz = 'utc'
            local = pytz.timezone(timezone_tz)
            local_dt = local.utcoffset(check_in_date)
        return check_in_date + local_dt

    @api.depends(
        'start_time'
    )
    def _compute_start_slot_time(self):
        for rec in self:
            if rec.start_time:
                date = self._convert_to_realtime(rec.start_time)
                a = date.time()
                total_time = (a.hour * 3600 + a.minute * 60 + a.second)/3600
                slot_id = self.env['helpdesk.slot'].sudo().search([('start_time','<=',total_time),('end_time','>=',total_time)], limit=1)
                if slot_id:
                    rec.start_slot_id = slot_id.id
                else:
#                    rec.start_time = False odoo13
                    rec.start_slot_id = False
            
    @api.depends(
        'end_time'
    )
    def _compute_end_slot_time(self):
        for rec in self:
            if rec.end_time:
                date = self._convert_to_realtime(rec.end_time)
                b = date.time()
                total_time = (b.hour * 3600 + b.minute * 60 + b.second)/3600
                slot_id = self.env['helpdesk.slot'].sudo().search([('start_time','<=',total_time),('end_time','>=',total_time)], limit=1)
                if slot_id:
                    rec.end_slot_id = slot_id.id
                else:
                    rec.end_slot_id =False
            

    start_slot_id = fields.Many2one(
        'helpdesk.slot',
        string="Start Slot",
        compute="_compute_start_slot_time",
        store=True
    )
    end_slot_id = fields.Many2one(
        'helpdesk.slot',
        string="End Slot",
        compute="_compute_end_slot_time",
        store=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='helpdesk_ticket_id.department_id',
        store=True
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='helpdesk_ticket_id.project_id',
        store=True
    )
    team_id = fields.Many2one(
        'support.team',
        string='Helpdesk Team',
        related='helpdesk_ticket_id.team_id',
        store=True
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        store=True,
        related='helpdesk_ticket_id.analytic_account_id'
    )
    type_ticket_id = fields.Many2one(
        'ticket.type',
        string="Type of Ticket",
        store=True,
        related='helpdesk_ticket_id.type_ticket_id',
    )
    subject_type_id = fields.Many2one(
        'type.of.subject',
        string="Type of Subject",
        store=True,
        related='helpdesk_ticket_id.subject_type_id',
    )
      
