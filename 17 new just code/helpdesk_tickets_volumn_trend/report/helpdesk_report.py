# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class ReportHelpDeskTicketTrend(models.Model):
    _name = 'report.helpdesk.ticket.trend'
    _description = "Ticket Trend"
    _order = 'name desc'
    _auto = False

    name = fields.Char(
        string='Ticket Title',
        readonly=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        readonly=True
    )
    request_date = fields.Datetime(
        string='Create Date',
        readonly=True
    )
    close_date = fields.Datetime(
        string='Close Date',
        readonly=True
    )    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        readonly=True
    )
    nbr = fields.Integer(
        '# of Ticket',
        readonly=True
    )
    priority = fields.Selection(
        selection=[
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High')
        ],
        readonly=True,
        string="Priority"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        readonly=True
    )
    stage_id = fields.Many2one(
        'helpdesk.stage.config',
        string='Stage',
        readonly=True
    )
    is_close = fields.Boolean(
        string='Is Ticket Closed',
        readonly=True
    )

    def _select(self):
        select_str = """
            SELECT
                (select 1 ) AS nbr,
                t.id as id,
                t.request_date as request_date,
                t.close_date as close_date,
                t.user_id,
                t.project_id,
                t.priority,
                t.name as name,
                t.company_id,
                t.partner_id,
                t.stage_id as stage_id,
                t.is_close as is_close
        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    t.id,
                    request_date,
                    close_date,
                    t.user_id,
                    t.project_id,
                    t.priority,
                    name,
                    t.company_id,
                    t.partner_id,
                    stage_id
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
              %s
              FROM helpdesk_support t
                %s
        """ % (self._table, self._select(), self._group_by()))
