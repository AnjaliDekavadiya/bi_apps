# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class HelpdeskSupport(models.Model):
    _inherit = 'helpdesk.support'

    stage_history_ids = fields.One2many(
        'helpdesk.stage.history',
        'helpdesk_ticket_id',
        string="Stage History",
    )
    level_config_id = fields.Many2one(
        'helpdesk.level.config',
        string="HelpDesk SLA Level",
    )
    dead_line_date = fields.Datetime(
        string="DeadLine Date",
    )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        for rec in self:
            rec.level_config_id = rec.partner_id.level_config_id

    @api.model
    def _get_stage_start_history(self, stage_id):
        TicketStageHistoryObj = self.env['helpdesk.stage.history'].sudo()
        domain = [
            ('helpdesk_ticket_id', '=', self.id),
            ('dest_stage_id', '=', stage_id)
        ]
        stage_start_line = TicketStageHistoryObj.search(domain)
        return stage_start_line

    @api.model
    def _compute_deadline(self, request_date, sla_level_id, vals):
        request_date = datetime.strptime(str(request_date), "%Y-%m-%d  %H:%M:%S")
        SLAObj = self.env['helpdesk.sla'].sudo()

        if vals.get('team_id', False):
            team_id = vals.get('team_id', False)
        elif self.team_id:
            team_id = self.team_id.id
        else:
            team_id = self.env['support.team'].sudo()._get_default_team_id(user_id=self.env.uid).id
        SLA_record = SLAObj.search([('helpdesk_team_id', '=', team_id)], limit=1)
        calendar_id = SLA_record.calendar_id
        company = self.env.user.company_id
        if vals.get('user_id', False):
            ticket_user = vals.get('user_id', False)
        elif self.user_id:
            ticket_user = self.user_id.id
        else:
            ticket_user = self._uid
        resource_domain = [
            ('calendar_id', '=', calendar_id.id),
            ('user_id', '=', ticket_user),
            ('company_id', '=', company.id),
            ('resource_type', '=', 'user'),
            ('active', '=', True),
        ]
        resource_id = self.env['resource.resource'].sudo().search(resource_domain,limit=1)
#        resource_id = resource_id and resource_id.id or False
        resource_id = resource_id or False

        dead_line_date = False
        if sla_level_id and resource_id:
            if vals.get('priority', False):
                priority = vals.get('priority', False)
            else:
                priority = self.priority
            if vals.get('category', False):
                category = vals.get('category', False)
            else:
                category = self.category
            line = sla_level_id.line_ids.filtered(lambda l: l.category == category and l.priority == priority)
            if line:
                interval = line.period_number
                if line.period_type == 'hours':
                    next_working_days = calendar_id.plan_hours(interval * 1.0,
                                                               day_dt=request_date,
                                                               compute_leaves=True,
                                                               resource=resource_id)
                    if next_working_days:
                        dead_line_date = next_working_days
#                     if next_working_days and next_working_days[0][0]:
#                         dead_line_date = next_working_days[0][0]
                elif line.period_type == 'days':
#                     next_working_days = calendar_id._get_next_work_day(day_date=request_date)\
                    next_working_days = calendar_id.plan_days(interval * 1.0,
                                                               day_dt=request_date,
                                                               compute_leaves=True,)
#                                                               resource=resource_id)
                    if next_working_days:
                        dead_line_date = next_working_days + timedelta(days=1)
                        
                elif line.period_type == 'weeks':
                    interval = line.period_number * 7
#                     week_request_date = request_date + relativedelta(days=interval)
#                     next_working_days = calendar_id._get_next_work_day(day_date=week_request_date)
#                     if next_working_days:
#                         dead_line_date = next_working_days

                    next_working_days = calendar_id.plan_days(interval * 1.0,
                                                               day_dt=request_date,
                                                               compute_leaves=True,)
#                                                               resource=resource_id)
                    if next_working_days:
                        dead_line_date = next_working_days + timedelta(days=1)

        return dead_line_date

    @api.model
    def create(self, vals):
        ticket = super(HelpdeskSupport, self).create(vals)

        TicketStageHistoryObj = self.env['helpdesk.stage.history']
        SLAObj = self.env['helpdesk.sla'].sudo()

        if ticket.stage_id:
            team_id = ticket.team_id
            if not team_id:
                team_id = self.env['support.team'].sudo()._get_default_team_id(user_id=self.env.uid)
            source_stage_id = ticket.stage_id.id
            if ticket.user_id:
                ticket_user = ticket.user_id.id
            else:
                ticket_user = self._uid
            history_vals = {
                    'stage_id': source_stage_id,
                    'dest_stage_id': source_stage_id,
                    'start_time': fields.Datetime.now(),
                    'user_id': ticket_user,
                    'team_id': team_id.id,
            }
            SLA_record = SLAObj.search([('helpdesk_team_id', '=', team_id.id)], limit=1)
            if SLA_record:
                sla_lines = SLA_record.sla_line_ids
#                     stage_validate_line = sla_lines.filtered(lambda l: l.source_stage_id.id == source_stage_id and l.destination_stage_id.id == dest_stage_id)
                stage_validate_line = sla_lines.filtered(lambda l: l.source_stage_id.id == source_stage_id)
                if stage_validate_line:
                    history_vals.update({
                        'estimate_time': stage_validate_line.service_time,
                        'calendar_id': stage_validate_line.sla_id.calendar_id.id
                    })
            ticket.write({'stage_history_ids': [(0, 0, history_vals)]})

        # compute deadline
        if ticket.request_date and ticket.level_config_id:
            dead_line_date = ticket._compute_deadline(ticket.request_date, ticket.level_config_id, vals)
            ticket.dead_line_date = dead_line_date
        return ticket

#    @api.multi odoo13
    def write(self, vals):
        SupportTeamObj = self.env['support.team'].sudo()
        SLAObj = self.env['helpdesk.sla'].sudo()
        TicketStageHistoryObj = self.env['helpdesk.stage.history']

        for ticket in self:
            # compute new deadline if it is not set in previous time
#             if not ticket.dead_line_date and not vals.get('dead_line_date', False):
                if vals.get('level_config_id', False) or vals.get('priority', False) or vals.get('category', False) or vals.get('team_id', False) or vals.get('user_id', False):
                    if vals.get('level_config_id', False):
                        sla_level_id = self.env['helpdesk.level.config'].sudo().browse(vals['level_config_id'])
                    else:
                        sla_level_id = ticket.level_config_id
#                     sla_level_id = self.env['helpdesk.level.config'].sudo().browse(level_config_id)
                    if ticket.request_date and sla_level_id:
                        dead_line_date = ticket._compute_deadline(ticket.request_date, sla_level_id, vals)
                        vals.update({'dead_line_date': dead_line_date})

        if vals.get('stage_id', False):
            for ticket in self:
                team_id = ticket.team_id
                if vals.get('team_id', False):
                    team_id = SupportTeamObj.browse(int(vals['team_id']))
                source_stage_id = ticket.stage_id.id
                dest_stage_id = vals['stage_id']

                stage_start_line = ticket._get_stage_start_history(source_stage_id)
                if stage_start_line:
                    stage_start_line.write({'end_time' :fields.Datetime.now()})
                if ticket.user_id:
                    ticket_user = ticket.user_id.id
                else:
                    ticket_user = self._uid
                history_vals = {
                    'helpdesk_ticket_id': ticket.id,
                    'stage_id': source_stage_id,
                    'dest_stage_id': dest_stage_id,
                    'start_time': fields.Datetime.now(),
                    'user_id': ticket_user,
                    'team_id': team_id.id,
                }
                SLA_record = SLAObj.search([('helpdesk_team_id', '=', team_id.id)], limit=1)
                if SLA_record:
                    sla_lines = SLA_record.sla_line_ids
                    stage_validate_line = sla_lines.filtered(lambda l: l.source_stage_id.id == dest_stage_id)
                    if stage_validate_line:
                        history_vals.update({
                            'estimate_time': stage_validate_line.service_time,
                            'calendar_id': stage_validate_line.sla_id.calendar_id.id
                        })
                history_line = TicketStageHistoryObj.create(history_vals)
        return super(HelpdeskSupport, self).write(vals)
