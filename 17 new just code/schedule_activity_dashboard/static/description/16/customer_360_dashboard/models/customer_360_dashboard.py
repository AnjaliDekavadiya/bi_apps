# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResPartner(models.Model):
    
    _inherit = 'res.partner'

    custom_sale_count = fields.Integer(
        compute='_compute_sales_count',
        readonly=True,
        default=0
    )

    custom_meeting_count = fields.Integer(
        compute='_compute_meetings_count',
        readonly=True,
        default=0
    )
    custom_invoice_count = fields.Integer(
        compute='_compute_invoices_count',
        readonly=True,
        default=0
    )
    custom_task_count = fields.Integer(
        compute='_compute_tasks_count',
        readonly=True,
        default=0
    )
    custom_project_count = fields.Integer(
        compute='_compute_projects_count',
        readonly=True,
        default=0
    )
    custom_analytic_count = fields.Integer(
        compute='_compute_analytics_count',
        readonly=True,
        default=0
    )
    custom_payment_count = fields.Integer(
        compute='_compute_payments_count',
        readonly=True,
        default=0
    )
    custom_opportunities_count = fields.Integer(
        compute='_compute_opportunities_count',
        readonly=True,
        default=0
    )

    # @api.multi
    def action_sale(self):
        action = self.env.ref('sale.act_res_partner_2_sale_order').sudo().read()[0]
        action['domain'] = [('partner_id', 'child_of', self.commercial_partner_id.id)]

        return action

    # @api.multi
    def action_invoice(self):
        # action = self.env.ref('account.action_invoice_refund_out_tree').sudo().read()[0]
        action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        action['domain'] = [('partner_id', 'child_of', self.commercial_partner_id.id)]

        return action

    # @api.multi
    def action_project(self):
        action = self.env.ref('project.open_view_project_all_config').sudo().read()[0]
        action['domain'] = [('partner_id', 'child_of', self.commercial_partner_id.id)]

        return action

    # @api.multi
    def action_task(self):
        action = self.env.ref('project.action_view_task').sudo().read()[0]
        action['domain'] = [('partner_id', 'child_of', self.commercial_partner_id.id)]

        return action

    # @api.multi
    def action_meetings(self):
        action = self.env.ref('calendar.action_calendar_event').sudo().read()[0]
        action['domain'] = [('partner_ids', 'child_of', self.commercial_partner_id.ids)]

        return action

    # @api.multi
    def action_opportunities(self):
        action = self.env.ref('crm.crm_lead_opportunities').sudo().read()[0]
        action['domain'] = [('partner_id', 'child_of', self.commercial_partner_id.id)]

        return action

    # @api.multi
    def action_analytic(self):
        # action = self.env.ref('account.action_open_partner_analytic_accounts').sudo().read()[0]
        action = self.env.ref('analytic.action_account_analytic_account_form').sudo().read()[0]
        action['domain'] = [('partner_id', 'child_of', self.commercial_partner_id.id)]

        return action

    # @api.multi
    def action_payment(self):
        action = self.env.ref('account.action_account_payments').sudo().read()[0]
        action['domain'] = [('partner_id', 'child_of', self.commercial_partner_id.id)]

        return action

    @api.depends()
    def _compute_sales_count(self):
        sale_order_records = self.env['sale.order']
        for record in self:
            record.custom_sale_count = sale_order_records.search_count([('partner_id', 'child_of', record.commercial_partner_id.id)])

    @api.depends()
    def _compute_tasks_count(self):
        project_task_records = self.env['project.task']
        for record in self:
            record.custom_task_count = project_task_records.search_count([('partner_id', 'child_of', record.commercial_partner_id.id)])

    @api.depends()
    def _compute_projects_count(self):
        project_records = self.env['project.project']
        for record in self:
            record.custom_project_count = project_records.search_count([('partner_id', 'child_of', record.commercial_partner_id.id)])


    @api.depends()
    def _compute_invoices_count(self):
        # account_invoice_records = self.env['account.invoice']
        account_invoice_records = self.env['account.move']
        for record in self:
            record.custom_invoice_count = account_invoice_records.search_count([('partner_id', 'child_of', record.commercial_partner_id.id)])


    @api.depends()
    def _compute_analytics_count(self):
        analytic_account_records = self.env['account.analytic.account']
        for record in self:
            record.custom_analytic_count = analytic_account_records.search_count([('partner_id', 'child_of', record.commercial_partner_id.id)])

    @api.depends()
    def _compute_meetings_count(self):
        meeting_records = self.env['calendar.event']
        for record in self:
            record.custom_meeting_count = meeting_records.search_count([('partner_ids', 'child_of', record.commercial_partner_id.ids)])


    @api.depends()
    def _compute_payments_count(self):
        payment_records = self.env['account.payment']
        for record in self:
            record.custom_payment_count = payment_records.search_count([('partner_id', 'child_of', record.commercial_partner_id.id)])


    @api.depends()
    def _compute_opportunities_count(self):
        opportunities_records = self.env['crm.lead']
        for record in self:
            record.custom_opportunities_count = opportunities_records.search_count([('partner_id', 'child_of', record.commercial_partner_id.id)])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
