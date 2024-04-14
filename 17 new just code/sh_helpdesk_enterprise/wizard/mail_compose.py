# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools import html2plaintext

class MailComposeWizard(models.TransientModel):
    _inherit = 'mail.compose.message'

    body_str = fields.Html('Body')
    is_wp = fields.Boolean('Whatsapp ?')

    def action_send_wp(self):
        # text = html2text.html2text(self.body)
        text = html2plaintext(self.body or "")
        if not self.partner_ids[0].mobile:
            raise UserError('Partner Mobile Number Not Exist !')
        phone = str(self.partner_ids[0].mobile)
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        if self.attachment_ids:
            text += '%0A%0A Other Attachments :'
            for attachment in self.attachment_ids:
                attachment.generate_access_token()
                text += '%0A%0A'
                text += base_url+'/web/content/ir.attachment/' + \
                    str(attachment.id)+'/datas?access_token=' + \
                    attachment.access_token
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        active_model = context.get('active_model', False)

        if text and active_id and active_model:
            message = str(text).replace('*', '').replace('_', '').replace(
                '%0A', '<br/>').replace('%20', ' ').replace('%26', '&')
            if active_model == 'helpdesk.ticket' and self.env[
                    'helpdesk.ticket'].browse(
                        active_id).company_id.sh_display_in_chatter:
                self.env['mail.message'].create({
                    'partner_ids': [(6, 0, self.partner_ids.ids)],
                    'model':
                    'helpdesk.ticket',
                    'res_id':
                    active_id,
                    'author_id':
                    self.env.user.partner_id.id,
                    'body':
                    message or False,
                    'message_type':
                    'comment',
                })
        url = "https://web.whatsapp.com/send?l=&phone=" + phone + "&text=" + text
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_send_mail(self):
        res = super(MailComposeWizard, self).action_send_mail()
        ticket_id = self.env['helpdesk.ticket'].search(
            [('id', 'in', self.env.context.get('active_ids'))])
        ticket_id.state = 'staff_replied'
        return res
