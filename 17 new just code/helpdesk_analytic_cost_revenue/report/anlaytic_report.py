# -*- coding: utf-8 -*-

from odoo import fields, models, tools


class ReportAccountAccount(models.Model):
    _name = "report.account.analytic.account"
    _description = "Analytic Account"
    _auto = False


    sale_cost_amount = fields.Float(
        string="Analytic Sales Amount",
        readonly=True
    )
    emplyee_cost_amount = fields.Float(
        string="Analytic Helpdesk Cost Amount",
        readonly=True
    )
    timesheet_cost_amount = fields.Float(
        string="Helpdesk Timesheet Cost",
        readonly=True
    )
    balance_cost_amount = fields.Float(
        string="Analytic Balance Amount",
        readonly=True
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        readonly=True
    )
    type_ticket_id = fields.Many2one(
        'ticket.type',
        string="Type of Ticket",
        readonly=True,
    )
    subject_type_id = fields.Many2one(
        'type.of.subject',
        string="Type of Subject",
        readonly=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assign To',
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        readonly=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department(H)'
    )
    team_id = fields.Many2one(
        'support.team',
        string='Helpdesk Team',
    )
    team_leader_id = fields.Many2one(
        'res.users',
        string='Team Leader',
    )
    service_support_type_id = fields.Many2one(
        'service.support.type',
        string='Billing Term',
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        string="Currency",
    )

#odoo13
#    start_date = fields.Date(
#        string="Start Date"
#    )
#odoo13
#    end_date = fields.Date(
#        string="End Date"
#    )
    helpdesk_support_id = fields.Many2one(
        'helpdesk.support',
        string="Helpdesk Support Ticket"
    )
    total_purchase_hours = fields.Float(
        string='Analytic Purchase Hours',
        store=True,
    )
    total_consumed_hours = fields.Float(
        string='Analytic Consumed Hours',
        store=True,
    )
    remaining_hours = fields.Float(
        string='Analytic Remaining Hours',
        store=True,
    )
    total_spend_hours = fields.Float(
        string='Helpdesk Hours Spent',
        store=True,
    )
    stage_id = fields.Many2one(
        'helpdesk.stage.config',
        string='Stage',
    )

    def _select(self):
        select_str = """
            SELECT
                a.id as analytic_account_id,                
                a.id as id,
                a.sale_cost_amount,
                a.emplyee_cost_amount,
                a.balance_cost_amount,
                jp.id as helpdesk_support_id,
                jp.timesheet_cost_amount,
                jp.type_ticket_id,
                jp.subject_type_id,
                jp.user_id,
                jp.company_id,
                jp.department_id,
                jp.team_id,
                jp.team_leader_id,
                jp.service_support_type_id,
                jp.custom_currency_id,
                jp.total_purchase_hours,
                jp.total_consumed_hours,
                jp.remaining_hours,
                jp.total_spend_hours,
                jp.stage_id

        """
        
#        def _select(self):
#        select_str = """
#            SELECT
#                a.id as analytic_account_id,                
#                a.id as id,
#                a.sale_cost_amount,
#                a.emplyee_cost_amount,
#                a.balance_cost_amount,
#                a.start_date,
#                a.end_date,
#                jp.id as helpdesk_support_id,
#                jp.timesheet_cost_amount,
#                jp.type_ticket_id,
#                jp.subject_type_id,
#                jp.user_id,
#                jp.company_id,
#                jp.department_id,
#                jp.team_id,
#                jp.team_leader_id,
#                jp.service_support_type_id,
#                jp.custom_currency_id,
#                jp.total_purchase_hours,
#                jp.total_consumed_hours,
#                jp.remaining_hours,
#                jp.total_spend_hours,
#                jp.stage_id

#        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    a.id,
                    a.sale_cost_amount,
                    a.emplyee_cost_amount,
                    a.balance_cost_amount,
                    jp.timesheet_cost_amount,
                    jp.type_ticket_id,
                    jp.subject_type_id,
                    jp.user_id,
                    jp.company_id,
                    jp.department_id,
                    jp.team_id,
                    jp.team_leader_id,
                    jp.service_support_type_id,
                    jp.custom_currency_id,
                    jp.id,
                    jp.total_purchase_hours,
                    jp.total_consumed_hours,
                    jp.remaining_hours,
                    jp.total_spend_hours,
                    jp.stage_id

        """
#odoo13
#        def _group_by(self):
#        group_by_str = """
#                GROUP BY
#                    a.id,
#                    a.sale_cost_amount,
#                    a.emplyee_cost_amount,
#                    a.balance_cost_amount,
#                    a.start_date,
#                    a.end_date,
#                    jp.timesheet_cost_amount,
#                    jp.type_ticket_id,
#                    jp.subject_type_id,
#                    jp.user_id,
#                    jp.company_id,
#                    jp.department_id,
#                    jp.team_id,
#                    jp.team_leader_id,
#                    jp.service_support_type_id,
#                    jp.custom_currency_id,
#                    jp.id,
#                    jp.total_purchase_hours,
#                    jp.total_consumed_hours,
#                    jp.remaining_hours,
#                    jp.total_spend_hours,
#                    jp.stage_id

#        """
        return group_by_str

    def _from(self):
        from_str = """
                account_analytic_account a
                left join helpdesk_support jp on (jp.analytic_account_id = a.id )
        """
        return from_str

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
              %s
              FROM  %s
                %s
        """ % (self._table, self._select(), self._from(), self._group_by()))
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
