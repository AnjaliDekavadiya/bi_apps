# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import models, fields, api


class HelpdeskStageHistory(models.Model):

    _inherit = 'helpdesk.stage.history'
    
#    @api.multi odoo13
    @api.depends(
        'overtime_hours',
        'working_time'
    )
    def _compute_custom_consumed_time(self):
        for rec in self:
            rec.custom_consumed_time = rec.overtime_hours + rec.working_time

    @api.depends(
        'consumed_time',
        'estimate_time'
    )
    def _compute_custom_delay_time(self):
        for line in self:
            if line.consumed_time > 0.0 and line.estimate_time > 0.0:
                line.custom_delay_time = line.consumed_time - line.estimate_time


    custom_delay_time = fields.Float(
        string="Delay(HH:MM)",
        compute="_compute_custom_delay_time",
        store=True,
    )
    
    custom_consumed_time = fields.Float(
        string="Consumed Time(HH:MM)",
        compute="_compute_custom_consumed_time",
        store=True,
    )
    
    custom_category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('support', 'Support')],
        string='Category',
        related ='helpdesk_ticket_id.category',
        store=True,
    )
    
    custom_partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related ='helpdesk_ticket_id.partner_id',
        store=True,
    )
    
    custom_close_date = fields.Datetime(
        string='Close Date',
        related ='helpdesk_ticket_id.close_date',
        store=True,
    )
    
    custom_user_id = fields.Many2one(
        'res.users',
        string='Assign To',
        related ='helpdesk_ticket_id.user_id',
        store=True,
    )
    
    custom_department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related ='helpdesk_ticket_id.department_id',
        store=True,
    )
    
    custom_project_id = fields.Many2one(
        'project.project',
        string='Project',
        related ='helpdesk_ticket_id.project_id',
        store=True,
    )
    
    custom_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        related ='helpdesk_ticket_id.analytic_account_id',
        store=True,
    )
    
    custom_team_leader_id = fields.Many2one(
        'res.users',
        string='Team Leader',
        related ='helpdesk_ticket_id.team_leader_id',
        store=True,
    )
    
    custom_level_config_id = fields.Many2one(
        'helpdesk.level.config',
        string="HelpDesk SLA Level",
        related ='helpdesk_ticket_id.level_config_id',
        store=True,
    )
    
    custom_dead_line_date = fields.Datetime(
        string="DeadLine Date",
        related ='helpdesk_ticket_id.dead_line_date',
        store=True,
    )
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
