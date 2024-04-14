# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class RepairReport(models.Model):
    _name = "repair.report"
    _description = "Repair Report"
    _auto = False

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
        'Technician', 
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
        'fleet.team',
        string='Repair Team',
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
        string='Is Repair Closed ?',
        # tracking=True,
        default=False,
        copy=False,
    )
    category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('repair', 'Repair')],
        string='Category',
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
    state = fields.Selection(
        [('new','New'),
         ('assigned','Assigned'),
         ('work_in_progress','Work in Progress'),
         ('needs_more_info','Needs More Info'),
         ('needs_reply','Needs Reply'),
         ('reopened','Reopened'),
         ('solution_suggested','Solution Suggested'),
         ('closed','Closed')],
        # tracking=True,
        default='new',
        copy=False, 
    )

#    @api.model_cr odoo13
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM %s 
            )""" % (self._table, self._select(), self._from()))

    def _select(self):
        select_str = """
                SELECT
                    c.id as id,
                    c.name as name,
                    c.request_date as request_date,
                    c.close_date as close_date,
                    c.user_id,
                    c.department_id,
                    c.is_close,
                    c.company_id as company_id,
                    c.priority as priority,
                    c.project_id as project_id,
                    c.subject as subject,
                    c.phone as phone,
                    c.team_id as team_id,
                    c.analytic_account_id as analytic_account_id,
                    c.category,
                    c.team_leader_id as team_leader_id,
                    c.partner_id,
                    c.state,
                    (SELECT count(id) FROM mail_message WHERE model='fleet.request' AND message_type IN ('email', 'comment') AND res_id=c.id) AS email

                """
        return select_str

    def _from(self):
        from_str = """
            fleet_request c
        """
        return from_str

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
