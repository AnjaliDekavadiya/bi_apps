# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from werkzeug.urls import url_encode


class InheritMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        values = super(InheritMessage, self).action_send_mail()
        work_list = []
        work_list_all = []
        work_obj = self.env['work.packages'].browse(self._context.get('active_id'))
        work_list.append(work_obj.id)
        work_obj1 = self.env['work.packages'].search([])
        for ids in work_obj1:
            work_list_all.append(ids.id)
        if work_list[0] in work_list_all:
            work_obj.state = 'sent'
        return


class WorkPackages(models.Model):
    _name = 'work.packages'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Work packages"

    name = fields.Char(string="Name")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('sent', 'Sent'),
        ('cancel', 'Cancel')
    ], readonly=True, default="draft")
    work_name = fields.Char(string='Work Number', readonly=True)
    project_id = fields.Many2one('project.project', string="Project")
    partner_id = fields.Many2one('res.partner', string="Customer")
    date = fields.Datetime(string="Date", default=datetime.now())
    user_id = fields.Many2one('res.users', string="Resposible User", index=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string="Company")
    internal_note = fields.Char("Internal note")
    work_pack_line_ids = fields.One2many('work.packages.line', 'work_pack_id', string="Work Packages Line")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['work_name'] = self.env['ir.sequence'].next_by_code('work.packages')
        return super(WorkPackages, self).create(vals_list)

    def approve_work_package(self):
        self.state = 'confirm'
        return True

    def action_rest(self):
        self.state = 'draft'
        return True

    def action_work_cancel(self):
        self.state = 'cancel'
        return True

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=True):
        self.ensure_one()
        if self.state not in ['confirm', 'sent']:
            auth_param = url_encode(self.partner_id.signup_get_auth_param()[self.partner_id.id])
            return self.get_portal_url(query_string='&%s' % auth_param)
        return super(WorkPackages, self)._get_share_url(redirect, signup_partner, pid, share_token)

    def _notify_get_groups(self, msg_vals=None):
        groups = super(WorkPackages, self)._notify_get_groups(msg_vals=msg_vals)
        self.ensure_one()
        if self.state not in ('draft', 'sent'):
            for group_name, group_method, group_data in groups:
                if group_name in ('customer', 'portal'):
                    continue
                group_data['has_button_access'] = True
        return groups

    def action_work_sent(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data._xmlid_lookup('bi_job_costing_work_package.email_template_edi_work')[1]
        compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[1]
        ctx = {
            'default_model': 'work.packages',
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx
        }


class WorkPackagesLine(models.Model):
    _name = 'work.packages.line'
    _description = "Work packages line"

    job_order_id = fields.Many2one('job.order', string="Job Order")
    work_pack_id = fields.Many2one('work.packages')
    job_id = fields.Char(string="Name")
    work_ids = fields.Char(string=" Job order", readonly=True)
    user_id = fields.Char(string="User Id", related="job_order_id.user_id.name")
    start_date = fields.Datetime(string="Start Date", related="job_order_id.start_date")
    end_date = fields.Datetime(string="End Date", related="job_order_id.end_date")
    planned_hours = fields.Float(string="Planned Hours", related='job_order_id.planned_hours')
    remaining_hours = fields.Float(string="Remaining hours", related='job_order_id.remaining_hours')


class InheritedJobOrder(models.Model):
    _inherit = 'job.order'

    work_packs_id = fields.Char(string="Sequence", readonly=True)
    packages_count = fields.Integer(' Scrap', compute='_get_packages_count')
    remaining_hours = fields.Float(string='remaining_hours')

    @api.onchange('timesheet_ids')
    def check_remaining_hours(self):
        units = []
        total_unit = 0
        for time in self.timesheet_ids:
            units = time.unit_amount
            total_unit = total_unit + units
        self.remaining_hours = self.planned_hours - total_unit

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['work_packs_id'] = self.env['ir.sequence'].get('job.order')
        return super(InheritedJobOrder, self).create(vals_list)

    def _get_packages_count(self):
        for pack in self:
            scrap_ids = self.env['work.packages.line'].search([('job_order_id', '=', pack.id)])
            pack.packages_count = len(scrap_ids)

    def pack_button(self):
        self.ensure_one()
        return {
            'name': 'work packages',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'work.packages',
        }


class InheritedProjectProject(models.Model):
    _inherit = 'project.project'

    packages_count = fields.Integer('Packages', compute='_get_packages_count')
    work_pack_id = fields.Many2one('work.packages')

    def _get_packages_count(self):
        for pack in self:
            scrap_ids = self.env['work.packages'].search([('project_id', '=', pack.id)])
            pack.packages_count = len(scrap_ids)

    def pack_button(self):
        self.ensure_one()
        return {
            'name': 'work packages',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'work.packages',
            'domain': [('project_id', '=', self.id)],
        }
