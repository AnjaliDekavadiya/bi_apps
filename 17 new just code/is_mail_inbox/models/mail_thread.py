# -*- coding: utf-8 -*-

import logging
import re
import email.policy

from xmlrpc import client as xmlrpclib

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):
        res = False
        try:
            res = super(MailThread, self).message_process(model=model, message=message, custom_values=custom_values,
                                          save_original=save_original, strip_attachments=strip_attachments,
                                          thread_id=thread_id)
        except ValueError as ve:
            pass

        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
        if isinstance(message, str):
            message = message.encode('utf-8')
        message = email.message_from_bytes(message, policy=email.policy.SMTP)
        original_message_id = message.get('Message-Id')
        # parse the message, verify we are not in a loop by checking message_id is not duplicated
        msg_dict = self.message_parse(message, save_original=save_original)

        if strip_attachments:
            msg_dict.pop('attachments', None)

        existing_msg_ids = self.env['mail.message'].search([('message_id', '=', msg_dict['message_id'])], limit=1)
        if existing_msg_ids:
            _logger.info('Ignored mail from %s to %s with Message-Id %s: found duplicated Message-Id during processing',
                         msg_dict.get('email_from'), msg_dict.get('to'), msg_dict.get('message_id'))
            return False

        if self._detect_loop_headers(msg_dict):
            return
        if msg_dict.get('message_type') == 'email':
            MailInbox = self.env['mail.inbox']
            email_from = msg_dict.get('email_from')
            email_cc = msg_dict.get('cc')
            email_to = msg_dict.get('to')
            match = re.match(r'"([^"]+)"', email_from)
            email_from_name = ''
            profile_pic = False
            try:
                partner_id = self.env['res.partner'].search([('email', '!=', False), ('email', '=', msg_dict.get('email_from'))], limit=1)
                profile_pic = partner_id and partner_id.image_128
            except:
                pass
            try:
                if match:
                    email_from_name = match.group(1)
                else:
                    email_from_name = email_from.split("@")[0]
            except Exception as e:
                pass
            email_data = {
                'subject': msg_dict.get('subject'),
                'body_html': msg_dict.get('body'),
                'email_from': email_from,
                'email_from_name': email_from_name,
                'email_cc': email_cc,
                'email_to': email_to,
                'reply_to': email_from,
                'date': msg_dict.get('date'),
                'state': 'received',
                'original_mail_message_id': original_message_id,
            }
            if profile_pic:
                email_data.update({'profile_pic': profile_pic})
            mail_id = False
            if not MailInbox.search_count([('original_mail_message_id', '=', original_message_id)]):
                mail_id = MailInbox.create(email_data)
            else:
                mail_id = MailInbox.write(email_data)
            attachments = msg_dict.get('attachments') or []
            if mail_id and attachments:
                attachment_ids = []
                msg_value = {
                    'body': msg_dict.get('body'),
                    'res_id': mail_id.id,
                    'model': mail_id._name,
                }
                attachement_values = self._message_post_process_attachments(attachments, attachment_ids, msg_value)
                if attachement_values:
                    mail_id.write({'attachment_ids': attachement_values.get('attachment_ids')})
        return res
