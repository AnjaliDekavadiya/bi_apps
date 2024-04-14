# -*- coding: utf-8 -*-
# from openerp import fields, models, api, _
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # @api.multi #odoo13
    def sent_mails(self):
        self.ensure_one()
        partner_ids = [self.id]

        if self.child_ids:
            partner_ids.extend(self.child_ids.ids)
        self._cr.execute("""
            SELECT
                mail_message_id
            FROM
                mail_message_res_partner_rel
            WHERE
                res_partner_id in %s
        """,(tuple(partner_ids),))
        other_messages = self._cr.dictfetchall()
        other_message_ids = [m['mail_message_id'] for m in other_messages]
        self._cr.execute("""
            SELECT
                message_id
            FROM
                res_partner_follower_mail_message_rel
            WHERE
                partner_id in %s
        """,(tuple(partner_ids),))
        messages_ids = self._cr.dictfetchall()
        message_ids = [m['message_id'] for m in messages_ids]
        other_message_ids.extend(message_ids)
        action = self.env.ref('mail.action_view_mail_message')
        action = action.sudo().read()[0]
        action['domain'] = [('id', 'in', tuple(other_message_ids))]
        return action

    # @api.multi #odoo13
    def received_mails(self):
        self.ensure_one()
        MailMessageObj = self.env['mail.message']
        message_ids = MailMessageObj.search(
            [('email_from', 'ilike', self.email)]).ids
        if self.child_ids:
            for child in self.child_ids:
                child_message_ids = MailMessageObj.search(
                    [('email_from', 'ilike', child.email)]).ids
                message_ids.extend(child_message_ids)
        action = self.env.ref('mail.action_view_mail_message')
        action = action.sudo().read()[0]
        action['domain'] = [('id', 'in', tuple(message_ids))]
        return action
