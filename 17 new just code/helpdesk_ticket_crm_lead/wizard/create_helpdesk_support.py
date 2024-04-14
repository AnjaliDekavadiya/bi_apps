# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class CreateHelpdeskSupportWizard(models.TransientModel):
    _name = 'create.helpdesk.support.wizard'
    _description = 'Create Helpdesk Support'

    type_ticket_id = fields.Many2one(
        'ticket.type',
        string="Type of Ticket",
        copy=False,
    )
    priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
        string='Priority',
        default='0'
    )
    category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('support', 'Support')],
        string='Category',
        required=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Assign To',
        tracking=True,
        required=True
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True
    )
    team_id = fields.Many2one(
        'support.team',
        string='Helpdesk Team',
        default=lambda self: self.env['support.team'].sudo()._get_default_team_id(user_id=self.env.uid),
        required=True
    )
    subject_type_id = fields.Many2one(
        'type.of.subject',
        string="Type of Subject",
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )
    custom_description = fields.Text(
        string="Description",
    )

#    @api.multi odoo13
    def create_helpdesk_ticket(self):
        context = self._context.copy()
        lead_id = self.env['crm.lead'].browse(int(context.get('active_id')))
        vals_allow_user_ids = []
        team_leader_id = lead_id.team_id.user_id
        for rec in self:
            vals_allow_user_ids.append((4, self.env.uid))
            if team_leader_id:
                vals_allow_user_ids.append((4, team_leader_id.id))
            analytic_account_id = rec.project_id.analytic_account_id
            vals = {
                'name': lead_id.name,
                'partner_id': lead_id.partner_id.id,
                'email': lead_id.email_from,
                'phone': lead_id.phone,
                'close_date': lead_id.date_deadline,
                'user_id': rec.user_id.id,
                'priority': rec.priority,
                'type_ticket_id': rec.type_ticket_id.id,
                'category': rec.category,
                'project_id': rec.project_id.id,
                'team_id': rec.team_id.id,
                'subject_type_id': rec.subject_type_id.id,
                'is_lead': True,
                'lead_id': lead_id.id,
                'lead_user_id': self.env.user.id,
                'allow_user_ids' : vals_allow_user_ids,
                'analytic_account_id' : analytic_account_id.id,
                'department_id' : rec.department_id.id,
                'description' : rec.custom_description,
            }
            ticket_id = False
            if not lead_id.is_create_ticket:
                ticket_id = self.env['helpdesk.support'].sudo().create(vals)
            if ticket_id:
                lead_id.is_create_ticket = True
            if self._context.get('open_ticket', False):
                return lead_id.action_open_helpdesk_ticket()
            return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
