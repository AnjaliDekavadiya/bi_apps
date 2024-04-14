# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HelpdeskSupportReassignWizard(models.TransientModel):
    _name = 'helpdesk.support.reassign.wizard'
    _description = 'Helpdesk Support Reassign Wizard'

    assign_to = fields.Selection(
        [('user','User'),
         ('team','Team')],
        string='Assign',
        required=True,
        default='user'
    )
    team_id = fields.Many2one(
        'support.team',
        string='Team',
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
    )

    # @api.multi #odoo13
    def action_reassign_support_ticket(self):
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', 'helpdesk.support')
        active_record = self.env[active_model].browse(active_id)
        context = self.env.context.copy()

        if self.assign_to == 'team':
            active_record.team_id = self.team_id.id
            active_record.user_id = self.team_id.leader_id.id
            active_record.team_leader_id = self.team_id.leader_id.id
            context.update({'team': True})
        else:
            active_record.user_id = self.user_id.id

        if active_record.user_id:
            email_tempalte = False
            try:
                email_tempalte = self.env.ref('helpdesk_support_ticket_reassign.email_template_reassign_ticket')
            except:
                email_tempalte = False

            if email_tempalte:
                email_tempalte.with_context(context).send_mail(active_record.id)
