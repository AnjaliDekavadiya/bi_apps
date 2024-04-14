# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta, MO,SU


class SupportTeam(models.Model):
    _inherit = "support.team"

    today = fields.date.today()
    start_dt = datetime.now().replace(hour=0, minute=0, second=0)
    end_dt = start_dt.replace(hour=23, minute=59, second=59)
    monday = (start_dt + relativedelta(weekday=MO(-1))).replace(hour=0, minute=0, second=0)
    sunday = (start_dt + relativedelta(weekday=SU(+1))).replace(hour=23, minute=59, second=59)
    first_day_this_month = (start_dt.replace(day=1)).replace(hour=0, minute=0, second=0)
    last_day_this_month = (datetime(start_dt.year,start_dt.month,1)+relativedelta(months=1,days=-1)).replace(hour=23, minute=59, second=59)
    last_month = start_dt - relativedelta(months=1)
    first_day_last_month = (last_month.replace(day=1)).replace(hour=0, minute=0, second=0)
    last_day_last_month = (datetime(last_month.year,last_month.month,1)+relativedelta(months=1,days=-1)).replace(hour=23, minute=59, second=59)

    this_day_new_ticket_count = fields.Integer(
        compute='_compute_this_day_new_ticket_count',
        string='Current Day New Ticket', readonly=True)
    this_week_new_ticket_count = fields.Integer(
        compute='_compute_this_week_new_ticket_count',
        string='Current Week New Ticket', readonly=True)
    this_month_new_ticket_count = fields.Integer(
        compute='_compute_this_month_new_ticket_count',
        string='Current Month New Ticket', readonly=True)
    last_month_new_ticket_count = fields.Integer(
        compute='_compute_last_month_new_ticket_count',
        string='Last Month New Ticket', readonly=True)

    this_day_to_assign_ticket_count = fields.Integer(
        compute='_compute_this_day_to_assign_ticket_count',
        string='Current Day To Assign Ticket', readonly=True)
    this_week_to_assign_ticket_count = fields.Integer(
        compute='_compute_this_week_to_assign_ticket_count',
        string='Current Week To Assign Ticket', readonly=True)
    this_month_to_assign_ticket_count = fields.Integer(
        compute='_compute_this_month_to_assign_ticket_count',
        string='Current Month To Assign Ticket', readonly=True)
    last_month_to_assign_ticket_count = fields.Integer(
        compute='_compute_last_month_to_assign_ticket_count',
        string='Last Month To Assign Ticket', readonly=True)

    this_day_close_ticket_count = fields.Integer(
        compute='_compute_this_day_close_ticket_count',
        string='Current Day Close Ticket', readonly=True)
    this_week_close_ticket_count = fields.Integer(
        compute='_compute_this_week_close_ticket_count',
        string='Current Week Close Ticket', readonly=True)
    this_month_close_ticket_count = fields.Integer(
        compute='_compute_this_month_close_ticket_count',
        string='Current Month Close Ticket', readonly=True)
    last_month_close_ticket_count = fields.Integer(
        compute='_compute_last_month_close_ticket_count',
        string='Last Month Close Ticket', readonly=True)
    
    this_day_deadline_ticket_count = fields.Integer(
        compute='_compute_this_day_deadline_ticket_count',
        string='Current Day Deadline Ticket', readonly=True)
    this_week_deadline_ticket_count = fields.Integer(
        compute='_compute_this_week_deadline_ticket_count',
        string='Current Week Deadline Ticket', readonly=True)
    this_month_deadline_ticket_count = fields.Integer(
        compute='_compute_this_month_deadline_ticket_count',
        string='Current Month Deadline Ticket', readonly=True)
    last_month_deadline_ticket_count = fields.Integer(
        compute='_compute_last_month_deadline_ticket_count',
        string='Last Month Deadline Ticket', readonly=True)

#        |----------------------------------------------|
#        |                 New Ticket                    |
#        |----------------------------------------------|

    def _compute_this_week_new_ticket_count(self):
        for rec in self:
            # Get a New Tickt in This Week
            domain = [
                ('request_date', '>=', self.monday.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.sunday.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', rec.id),
            ]
            new_tickt_this_week = self.env['helpdesk.support'].search(domain).ids
            if new_tickt_this_week:
                rec.this_week_new_ticket_count = len(new_tickt_this_week)
            else:
                rec.this_week_new_ticket_count = 0

    def _compute_this_month_new_ticket_count(self):
        for rec in self:
            domain = [
                ('request_date', '>=', self.first_day_this_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.last_day_this_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
            ]
            new_tickt_this_month = self.env['helpdesk.support'].search(domain).ids
            if new_tickt_this_month:
                rec.this_month_new_ticket_count = len(new_tickt_this_month)
            else:
                rec.this_month_new_ticket_count = 0

    def _compute_last_month_new_ticket_count(self):
        for rec in self:
            domain = [
                ('request_date', '>=', self.first_day_last_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.last_day_last_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
            ]
            new_tickt_last_month = self.env['helpdesk.support'].search(domain).ids
            
            if new_tickt_last_month:
                rec.last_month_new_ticket_count = len(new_tickt_last_month)
            else:
                rec.last_month_new_ticket_count = 0

    def _compute_this_day_new_ticket_count(self):
        # Get a New Tickt in This Day
        for rec in self:
            domain = [
                ('request_date', '>=', self.start_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.end_dt.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
            ]
            new_tickt_this_day = self.env['helpdesk.support'].search(domain).ids
            
            if new_tickt_this_day:
                rec.this_day_new_ticket_count = len(new_tickt_this_day)
            else:
                rec.this_day_new_ticket_count = 0

    def new_tickt_this_day(self):
#        context = self.env.context.copy()
        domain = [
                ('request_date', '>=', self.start_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.end_dt.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_day_new_ticket': 1}
        return result

    def new_tickt_this_week(self):
#        context = self.env.context.copy()
        domain = [
            ('request_date', '>=', self.monday.strftime("%Y-%m-%d %H:%M:%S")),
            ('request_date', '<=', self.sunday.strftime("%Y-%m-%d %H:%M:%S")),
            ('team_id', '=', self.id),
        ]
#        ticket_id = self.env['helpdesk.support'].search([('team_id', '=', self.id)])
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_week_new_ticket': 1}
        return result

    def new_tickt_this_month(self):
        domain = [
                ('request_date', '>=', self.first_day_this_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.last_day_this_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
            ]
#        context = self.env.context.copy()
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_month_new_ticket': 1}
        return result

    def new_tickt_this_last_month(self):
#        context = self.env.context.copy()
        domain = [
                ('request_date', '>=', self.first_day_last_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.last_day_last_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_last_month_new_ticket': 1}
        return result

#        |----------------------------------------------|
#        |                 Assign To                    |
#        |----------------------------------------------|

    def _compute_this_day_to_assign_ticket_count(self):
        for rec in self:
            # Get a Assign To in This Day
            domain = [
                ('request_date', '>=', self.start_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.end_dt.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
                ('user_id', '=', False)
            ]
            assign_to_this_day = self.env['helpdesk.support'].search(domain).ids
            
            if assign_to_this_day:
                rec.this_day_to_assign_ticket_count = len(assign_to_this_day)
            else:
                rec.this_day_to_assign_ticket_count = 0

    def _compute_this_week_to_assign_ticket_count(self):
        for rec in self:
            # Get a Assign To in This Week
            domain = [
                ('request_date', '>=', self.monday.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.sunday.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', rec.id),
                ('user_id', '=', False)
            ]
            assign_to_this_week = self.env['helpdesk.support'].search(domain).ids
            
            if assign_to_this_week:
                rec.this_week_to_assign_ticket_count = len(assign_to_this_week)
            else:
                rec.this_week_to_assign_ticket_count = 0

    def _compute_this_month_to_assign_ticket_count(self):
        for rec in self:
            # Get a Assign To in This Month
            domain = [
                ('request_date', '>=', self.first_day_this_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.last_day_this_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
                ('user_id', '=', False)
            ]
            assign_to_this_month = self.env['helpdesk.support'].search(domain).ids
            
            if assign_to_this_month:
                rec.this_month_to_assign_ticket_count = len(assign_to_this_month)
            else:
                rec.this_month_to_assign_ticket_count = 0

    def _compute_last_month_to_assign_ticket_count(self):
        for rec in self:
            # Get a Assign To in Last Month
            domain = [
                ('request_date', '>=', self.first_day_last_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.last_day_last_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
                ('user_id', '=', False)
            ]
            assign_to_last_month = self.env['helpdesk.support'].search(domain).ids
            
            if assign_to_last_month:
                rec.last_month_to_assign_ticket_count = len(assign_to_last_month)
            else:
                rec.last_month_to_assign_ticket_count = 0

    def assigned_to_this_day(self):
        domain = [
                ('request_date', '>=', self.start_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.end_dt.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
                ('user_id', '=', False)
            ]
#        context = self.env.context.copy()
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_day_assigned_to': 1}
        return result

    def assigned_to_this_week(self):
        domain = [
                ('request_date', '>=', self.monday.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.sunday.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', self.id),
                ('user_id', '=', False)
            ]
#        context = self.env.context.copy()
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_week_assigned_to': 1}
        return result

    def assigned_to_this_month(self):
#        context = self.env.context.copy()
        domain = [
                ('request_date', '>=', self.first_day_this_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.last_day_this_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
                ('user_id', '=', False)
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_month_assigned_to': 1}
        return result

    def assigned_to_last_month(self):
#        context = self.env.context.copy()
        domain = [
                ('request_date', '>=', self.first_day_last_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('request_date', '<=', self.last_day_last_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
                ('user_id', '=', False)
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_last_month_assigned_to': 1}
        return result

#        |----------------------------------------------|
#        |                 Close Ticket                 |
#        |----------------------------------------------|

    def _compute_this_day_close_ticket_count(self):
        for rec in self:
            # Get a Close Ticket in This Day
            domain = [
                ('close_date', '>=', self.start_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('close_date', '<=', self.end_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', rec.id),
                ('stage_type', '=', 'closed')
            ]
            close_ticket_this_day = self.env['helpdesk.support'].search(domain).ids
            
            if close_ticket_this_day:
                rec.this_day_close_ticket_count = len(close_ticket_this_day)
            else:
                rec.this_day_close_ticket_count = 0

    def _compute_this_week_close_ticket_count(self):
        for rec in self:
            # Get a Close Ticket in This Week
            domain = [
                ('close_date', '>=', self.monday.strftime("%Y-%m-%d %H:%M:%S")),
                ('close_date', '<=', self.sunday.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', rec.id),
                ('stage_type', '=', 'closed')
            ]
            close_ticket_this_week = self.env['helpdesk.support'].search(domain).ids
            
            if close_ticket_this_week:
                rec.this_week_close_ticket_count = len(close_ticket_this_week)
            else:
                rec.this_week_close_ticket_count = 0

    def _compute_this_month_close_ticket_count(self):
        for rec in self:
            # Get a Close Ticket in This Month
            domain = [
                ('close_date', '>=', self.first_day_this_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('close_date', '<=', self.last_day_this_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
                ('stage_type', '=', 'closed')
            ]
            close_ticket_this_month = self.env['helpdesk.support'].search(domain).ids
            
            if close_ticket_this_month:
                rec.this_month_close_ticket_count = len(close_ticket_this_month)
            else:
                rec.this_month_close_ticket_count = 0

    def _compute_last_month_close_ticket_count(self):
        for rec in self:
            # Get a Close Ticket in Last Month
            domain = [
                ('close_date', '>=', self.first_day_last_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('close_date', '<=', self.last_day_last_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
                ('stage_type', '=', 'closed')
            ]
            close_ticket_last_month = self.env['helpdesk.support'].search(domain).ids
            
            if close_ticket_last_month:
                rec.last_month_close_ticket_count = len(close_ticket_last_month)
            else:
                rec.last_month_close_ticket_count = 0

    def close_this_day(self):
#        context = self.env.context.copy()
        domain = [
                ('close_date', '>=', self.start_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('close_date', '<=', self.end_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', self.id),
                ('stage_type', '=', 'closed')
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        print('ticket_id=====================>',ticket_id)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_day_close': 1}
        return result

    def close_this_week(self):
#        context = self.env.context.copy()
        domain = [
                ('close_date', '>=', self.monday.strftime("%Y-%m-%d %H:%M:%S")),
                ('close_date', '<=', self.sunday.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', self.id),
                ('stage_type', '=', 'closed')
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_week_close': 1}
        return result

    def close_ticket_this_month(self):
#        context = self.env.context.copy()
        domain = [
                ('close_date', '>=', self.first_day_this_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('close_date', '<=', self.last_day_this_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
                ('stage_type', '=', 'closed')
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_month_close': 1}
        return result

    def close_ticket_last_month(self):
#        context = self.env.context.copy()
        domain = [
                ('close_date', '>=', self.first_day_last_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('close_date', '<=', self.last_day_last_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
                ('stage_type', '=', 'closed')
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
        result['context'] = {'search_default_last_month_close': 1}
        return result
    

#        |----------------------------------------------|
#        |                 Deadline Ticket                 |
#        |----------------------------------------------|
    
    def _compute_this_day_deadline_ticket_count(self):
        for rec in self:
            # Get a Close Ticket in This Day
            domain = [
                ('dead_line_date', '>=', self.start_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('dead_line_date', '<=', self.end_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', rec.id),
                ('stage_type', '!=', 'closed')
            ]
            close_ticket_this_day = self.env['helpdesk.support'].search(domain).ids
            
            if close_ticket_this_day:
                rec.this_day_deadline_ticket_count = len(close_ticket_this_day)
            else:
                rec.this_day_deadline_ticket_count = 0

    def _compute_this_week_deadline_ticket_count(self):
        for rec in self:
            # Get a Close Ticket in This Week
            domain = [
                ('dead_line_date', '>=', self.monday.strftime("%Y-%m-%d %H:%M:%S")),
                ('dead_line_date', '<=', self.sunday.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', rec.id),
                ('stage_type', '!=', 'closed')
            ]
            close_ticket_this_week = self.env['helpdesk.support'].search(domain).ids
            
            
            if close_ticket_this_week:
                rec.this_week_deadline_ticket_count = len(close_ticket_this_week)
            else:
                rec.this_week_deadline_ticket_count = 0

    def _compute_this_month_deadline_ticket_count(self):
        for rec in self:
            # Get a Close Ticket in This Month
            domain = [
                ('dead_line_date', '>=', self.first_day_this_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('dead_line_date', '<=', self.last_day_this_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
                ('stage_type', '!=', 'closed')
            ]
            close_ticket_this_month = self.env['helpdesk.support'].search(domain).ids
            
            if close_ticket_this_month:
                rec.this_month_deadline_ticket_count = len(close_ticket_this_month)
            else:
                rec.this_month_deadline_ticket_count = 0

    def _compute_last_month_deadline_ticket_count(self):
        for rec in self:
            # Get a Close Ticket in Last Month
            domain = [
                ('dead_line_date', '>=', self.first_day_last_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('dead_line_date', '<=', self.last_day_last_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', rec.id),
                ('stage_type', '!=', 'closed')
            ]
            close_ticket_last_month = self.env['helpdesk.support'].search(domain).ids
            
            if close_ticket_last_month:
                rec.last_month_deadline_ticket_count = len(close_ticket_last_month)
            else:
                rec.last_month_deadline_ticket_count = 0
    
    def this_day_deadline_ticket(self):
#        context = self.env.context.copy()
        domain = [
                ('dead_line_date', '>=', self.start_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('dead_line_date', '<=', self.end_dt.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', self.id),
                ('stage_type', '!=', 'closed')
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_day_deadline': 1}
        return result

    def deadline_this_week(self):
#        context = self.env.context.copy()
        domain = [
                ('dead_line_date', '>=', self.monday.strftime("%Y-%m-%d %H:%M:%S")),
                ('dead_line_date', '<=', self.sunday.strftime("%Y-%m-%d %H:%M:%S")),
                ('team_id', '=', self.id),
                ('stage_type', '!=', 'closed')
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_week_deadline': 1}
        return result

    def deadline_ticket_this_month(self):
#        context = self.env.context.copy()
        domain = [
                ('dead_line_date', '>=', self.first_day_this_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('dead_line_date', '<=', self.last_day_this_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
                ('stage_type', '!=', 'closed')
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_this_month_deadline': 1}
        return result

    def deadline_ticket_last_month(self):
#        context = self.env.context.copy()
        domain = [
                ('dead_line_date', '>=', self.first_day_last_month.strftime("%Y-%m-%d %H:%M:%S")),
                ('dead_line_date', '<=', self.last_day_last_month.date().strftime("%Y-%m-%d")),
                ('team_id', '=', self.id),
                ('stage_type', '!=', 'closed')
            ]
        ticket_id = self.env['helpdesk.support'].search(domain)
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('id', 'in', ticket_id.ids)]
#        result['context'] = {'search_default_last_month_deadline': 1}
        return result

    def action_jump_to_ticket(self):
        # action = self.env.ref('website_helpdesk_support_ticket.action_helpdesk_support')
        # result = action.sudo().read()[0]
        result = self.env['ir.actions.act_window']._for_xml_id('website_helpdesk_support_ticket.action_helpdesk_support')
        result['domain'] = [('team_id', '=', self.id)]
        result['context'] = {'default_team_id': self.id}
        return result
    
    
    def action_create_ticket(self):
        context = self.env.context.copy()
        context.update({'default_team_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.support',
            'view_mode': 'form',
            'res_id': False,
            'target': 'current',
            'context': context,
            'flags': {
                'form': {
                    'action_buttons': True,
                    'options': {
                        'mode': 'create'
                    }
                }
            }
        }
