# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import models, api ,fields

class HelpdeskSupport(models.Model):
    _inherit = "helpdesk.support"

    stage_id = fields.Many2one(
        'helpdesk.stage.config',
        tracking=True
    )
    
#     def send_mail_responsible_user(self, stage_id, rec, ctx):
#         send_to = ''
#         if stage_id.is_auto_response:
#             if stage_id.to_customer and rec.partner_id:
#                 if rec.partner_id.email and not rec.partner_id.email in send_to:
#                     if send_to == '':
#                         send_to += rec.partner_id.email
#                     else:
#                         send_to += ',' + rec.partner_id.email
                
#             if stage_id.document_follower and rec.message_partner_ids:
#                 for message_partner_id in rec.message_partner_ids:
#                     if not (message_partner_id == rec.partner_id and stage_id.to_customer):
#                         if message_partner_id.email and not message_partner_id.email in send_to:
#                             if send_to == '':
#                                 send_to += message_partner_id.email
#                             else:
#                                 send_to += ',' + message_partner_id.email
#             if stage_id.internal_users:
#                 for user in stage_id.internal_user_ids:
#                     if user.email and not user.email in send_to:
#                         if send_to == '':
#                             send_to += user.email
#                         else:
#                             send_to += ',' + user.email
#             if send_to != '':
#                 ctx.update({
#                     'email_to':send_to,
#                 })
#                 email_values={
#                     'email_to':send_to,
#                 }
#                 try:
#                     stage_id.custom_tempalte_id.with_context(
#                         ctx
#                     ).send_mail(rec.id,
#                     email_values=email_values, force_send=True)
#                 except:
#                     pass
#         return True

#     @api.model
#     def create(self, vals):
#         res = super(HelpdeskSupport, self).create(vals)
#         if res.stage_id.is_auto_response:
#             ctx = self._context.copy()
#             ctx.update({
#                'ticket_name':res.name,
#                'ticket_subject':res.subject,
#                'stage':res.stage_id.name,
#                'old_stage': 'create'
#             })
#             # ctx={
#             #     'ticket_name':res.name,
#             #     'ticket_subject':res.subject,
#             #     'stage':res.stage_id.name,
#             #     'old_stage': 'create'
#             # }
#             self.send_mail_responsible_user(res.stage_id, res, ctx)
#         return res

# #    @api.multi odoo13
#     def write(self, vals):
#         for rec in self:
#             ctx = self._context.copy()
#             ctx.update({'old_stage': rec.stage_id.name})
#             # ctx = {'old_stage': rec.stage_id.name}
#             if "stage_id" in vals:
#                 stage_id = rec.env['helpdesk.stage.config'].browse(vals.get('stage_id'))
#                 ctx.update({
#                     'ticket_name':rec.name,
#                     'ticket_subject':rec.subject,
#                     'stage':stage_id.name,
#                 })
#                 send_to = ''
#                 if stage_id.is_auto_response:
#                     self.send_mail_responsible_user(stage_id, rec, ctx)
#         return super(HelpdeskSupport, self).write(vals) 


    def _track_template(self, changes):
        res = super(HelpdeskSupport, self)._track_template(changes)
        ticket = self[0]
        if 'stage_id' in changes and ticket.stage_id.is_auto_response and ticket.stage_id.custom_tempalte_id:
            res['stage_id'] = (ticket.stage_id.custom_tempalte_id, {
                # 'auto_delete_message': True,
                'auto_delete_keep_log': True,
                # 'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
                'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note', raise_if_not_found=False),
                'email_layout_xmlid': 'mail.mail_notification_light'
            })
        return res

    @api.model
    def create(self, vals):
        if vals.get('team_id'):
            custom_stage = self._stage_find(team_id=vals['team_id'], domain=[('fold', '=', False)]).id
            if 'stage_id' not in vals and custom_stage: 
                vals.update({
                    'stage_id': custom_stage
                    })
        else:
            custom_stage = self._stage_find(team_id=False, domain=[('fold', '=', False)]).id
            if 'stage_id' not in vals and custom_stage: 
                vals.update({
                    'stage_id': custom_stage
                    })
        return super(HelpdeskSupport, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: