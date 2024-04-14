# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, api,fields, _

class heldpeskTicketChild(models.TransientModel):
    _name = 'heldpesk.ticket.child.wizard'
    _description = 'Helpdesk Ticket Child Wizard'

    custom_subject = fields.Char(
        string="Subject",
        required=True
    )
    custom_type_ticket_id = fields.Many2one(
        'ticket.type',
        string="Type of Ticket",
        copy=False,
        required=True
    )
    custom_user_id = fields.Many2one(
        'res.users',
        string='Assign To',
        required=True
    )
    custom_team_id = fields.Many2one(
        'support.team',
        string='Helpdesk Team',
        default=lambda self: self.env['support.team'].sudo()._get_default_team_id(user_id=self.env.uid),
        required=True
    )
    custom_priority = fields.Selection(
        [('0', 'Low'),
        ('1', 'Middle'),
        ('2', 'High')],
        string='Priority',
        required=True
    )
    custom_category = fields.Selection(
        [('technical', 'Technical'),
        ('functional', 'Functional'),
        ('support', 'Support')],
        string='Category',
        required=True
    )
    custom_description = fields.Text(
        string="Description",
    )
    custom_subject_type_id = fields.Many2one(
        'type.of.subject',
        string="Type of Subject",
        copy=True,
        required=True
    )
    custom_department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True
    )



    # @api.multi #odoo13
    def create_child_ticket(self):
        context = dict(self._context or {})
        active_id = self._context.get('active_id', False)
        for record in self.env['helpdesk.support'].browse(active_id):
            for ticket in self:
                helpdesk_support_vals = {
                    'subject' : ticket.custom_subject,
                    'type_ticket_id': ticket.custom_type_ticket_id.id,
                    'user_id' : ticket.custom_user_id.id,
                    'team_id' : ticket.custom_team_id.id,
                    'project_id' : record.project_id.id,
                    'partner_id' : record.partner_id.id,
                    'priority' : ticket.custom_priority,
                    'category' : ticket.custom_category,
                    'description' : ticket.custom_description,
                    'custom_parent_id' : record.id,
                    'subject_type_id' : ticket.custom_subject_type_id.id,
                    'email' : record.email,
                    'company_id' : record.company_id.id,
                    'department_id' : ticket.custom_department_id.id,
                    'phone' : record.phone,
                    'allow_user_ids' : record.allow_user_ids.ids,
                    'analytic_account_id' : record.analytic_account_id.id,
                    }
                helpdesk_support_id= self.env['helpdesk.support'].create(helpdesk_support_vals)
                if helpdesk_support_id:      

                    action = {
                    'type': 'ir.actions.act_window',
                    'res_model': 'helpdesk.support',
                    'target': 'current',
                        }

                    new_helpdesk_support_id = self.env['helpdesk.support'].search([('id', '=', helpdesk_support_id.id)])
                    if new_helpdesk_support_id:
                        action['res_id'] = new_helpdesk_support_id.ids[0]
                        action['view_mode'] = 'form'
                        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: