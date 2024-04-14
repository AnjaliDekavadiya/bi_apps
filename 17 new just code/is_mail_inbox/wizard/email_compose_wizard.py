# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class EmailCompose(models.TransientModel):
    _name = "email.compose.wizard"
    _description = "Email Compose Wizard"

    @api.model
    def default_get(self, fields):
        result = super(EmailCompose, self).default_get(fields)
        missing_author = 'author_id' in fields and 'author_id' not in result
        missing_email_from = 'email_from' in fields and 'email_from' not in result
        if missing_author or missing_email_from:
            author_id, email_from = self.env['mail.thread']._message_compute_author(result.get('author_id'), result.get('email_from'), raise_on_email=False)
            if missing_email_from:
                result['email_from'] = email_from
            if missing_author:
                result['author_id'] = author_id
        if 'create_uid' in fields and 'create_uid' not in result:
            result['create_uid'] = self.env.uid
        re_prefix = subject = _('Re:')
        if result.get('parent_id'):
            parent_mail = self.env['mail.inbox'].browse(result.get('parent_id'))
            if parent_mail:
                subject = tools.ustr(parent_mail.subject)
                result['reply_to'] = parent_mail.reply_to or parent_mail.email_from
        if subject and not (subject.startswith('Re:') or subject.startswith(re_prefix)):
            subject = "%s %s" % (re_prefix, subject)
        result['subject'] = subject
        return result

    subject = fields.Char('Subject', compute=False)
    body = fields.Html('Contents', render_engine='qweb', compute=False, default='', sanitize_style=True)
    parent_id = fields.Many2one(
        'mail.inbox', 'Parent Email', ondelete='set null')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'email_compose_wizard_ir_attachments_rel',
        'email_wizard_id', 'attachment_id', 'Attachments')
    email_add_signature = fields.Boolean(default=True)
    email_from = fields.Char('From', help="Email address of the sender. This field is set when no matching partner is found and replaces the author_id field in the chatter.")
    author_id = fields.Many2one(
        'res.partner', 'Author',
        help="Author of the message. If not set, email_from may hold an email address that did not match any partner.")
    reply_to = fields.Char('Reply To', help='Reply email address.')
    reply_to_force_new = fields.Boolean(
        string='Considers answers as new thread',
        help='Manage answers as new incoming emails instead of replies going to the same thread.')
    reply_to_mode = fields.Selection([
        ('update', 'Store email and replies in the chatter of each record'),
        ('new', 'Collect replies on a specific email address')],
        string='Replies', compute='_compute_reply_to_mode', inverse='_inverse_reply_to_mode',
        help="Original Discussion: Answers go in the original document discussion thread. \n Another Email Address: Answers go to the email address mentioned in the tracking message-id instead of original document discussion thread. \n This has an impact on the generated message-id.")
    auto_delete = fields.Boolean('Delete Emails',
        help='This option permanently removes any track of email after it\'s been sent, including from the Technical menu in the Settings, in order to preserve storage space of your Odoo database.')
    auto_delete_message = fields.Boolean('Delete Message Copy', help='Do not keep a copy of the email in the document communication history (mass mailing only)')
    mail_server_id = fields.Many2one('ir.mail_server', 'Outgoing mail server')

    def action_send_mail(self):
        mail_values = {
            'subject': self.subject,
            'body': self.body or '',
            'email_to': self.reply_to,
            # 'parent_id': self.parent_id and self.parent_id.id,
            # 'partner_ids': [partner.id for partner in self.partner_ids],
            'attachment_ids': [attach.id for attach in self.attachment_ids],
            'author_id': self.author_id.id,
            'email_from': self.email_from,
            'reply_to_force_new': self.reply_to_force_new,
            'mail_server_id': self.parent_id.mail_server_id.id,
            'message_type': 'email',
            'body_html': self.body or '',
            'auto_delete': False,
        }
        headers = self._notify_by_email_get_headers()
        if headers:
            headers["References"] = self.parent_id.original_mail_message_id
            headers["In-Reply-To"] = self.parent_id.original_mail_message_id
            mail_values['headers'] = repr(headers)
        mail_id = self.env['mail.inbox'].create(mail_values)
        mail_id.send()
