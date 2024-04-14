# -*- coding: utf-8 -*-

from odoo import api, fields, models,tools

class LaundryServiceReport(models.Model):
    _name = "laundry.service.report"
    _auto = False
    _description = "Laundry Service Report"

    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        readonly=True
    )
    priority = fields.Selection(
        [('0', 'Low'), 
        ('1', 'Normal'), 
        ('2', 'High')],
    )
    project_id = fields.Many2one(
        'project.project', 
        'Project', 
        readonly=True
    )
    user_id = fields.Many2one(
        'res.users', 
        'Assigned to', 
        readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner', 
        'Contact'
    )
    email = fields.Char(
        'Emails',
         readonly=True
     )
    phone = fields.Char(
        string="Phone"
    )
    name = fields.Char(
        string='Number', 
        required=True, 
        copy=False, 
        readonly=True, 
    )
    subject = fields.Char(
        string="Subject"
    )
    team_id = fields.Many2one(
        'laundry.business.team',
        string='Laundry Team',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )
    team_leader_id = fields.Many2one(
        'res.users',
        string='Team Leader',
        related ='team_id.leader_id',
        store=True,
    )
    close_date = fields.Datetime(
        string='Close Date',
    )
    is_close = fields.Boolean(
        string='Is Request Closed ?',
        tracking=True,
        default=False,
        copy=False,
    )
    request_date = fields.Datetime(
        string='Create Date',
        default=fields.date.today(),
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    stage_id = fields.Many2one(
        'laundry.stage.custom',
        string="Stage",
        ondelete='restrict',
        tracking=True, 
    )
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
