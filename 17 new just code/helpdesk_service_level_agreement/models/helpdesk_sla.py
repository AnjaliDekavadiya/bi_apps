# -*- coding: utf-8 -*-

from odoo import models, fields


class HelpdeskSla(models.Model):
    _name = 'helpdesk.sla'
    _description = 'Service Level Agreement'

    name = fields.Char(
        'Name',
        required=True,
    )
    helpdesk_team_id = fields.Many2one(
        'support.team',
        'Helpdesk Team',
        required=True,
    )
    sla_line_ids = fields.One2many(
        'helpdesk.sla.line',
        'sla_id',
        'SLA Lines',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company', 
        default=lambda self: self.env.user.company_id, 
        string='Company',
        readonly=True,
    )
    calendar_id = fields.Many2one(
        'resource.calendar',
        'Resource Calendar',
        required=True,
    )
    notes = fields.Text(
        'Add comment'
    )


class HelpdeskSlaLine(models.Model):
    _name = 'helpdesk.sla.line'
    _description = 'Service Level Agreement Lines'
    
    source_stage_id = fields.Many2one(
        'helpdesk.stage.config',
        string="Stage From",
        required=True,
    )
    destination_stage_id = fields.Many2one(
        'helpdesk.stage.config',
        string="Stage To",
        required=False,
    )
    service_time = fields.Float(
        'Time',
        copy=False,
        required=True
    )
    is_email = fields.Boolean(
        'Email',
        copy=False,
    )
    sla_id = fields.Many2one(
        'helpdesk.sla',
        'Services'
    )
