# -*- coding: utf-8 -*-

import ast
import base64
import logging
import psycopg2
import smtplib
import re

from odoo import _, api, fields, models, tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class MailInbox(models.Model):
    _name = 'mail.inbox'
    _inherit = 'mail.mail'
    _description = 'Mail Inbox'
    _rec_name = 'subject'
    _order = 'date desc, id desc'

    is_read = fields.Boolean()
    subject = fields.Char('Subject')
    date = fields.Datetime('Date', default=fields.Datetime.now)
    body_html = fields.Text('Text Contents', help="Rich-text/HTML message")
    body_content = fields.Html('Body', sanitize=True, compute='_compute_body_content', search="_search_body_content")
    email_from = fields.Char('From', help="Email address of the sender.", default=lambda self: self.env.user.email_formatted)
    email_from_name = fields.Char('From Name')
    email_to_name = fields.Char('Email To Name')
    email_bcc = fields.Char('Bcc', help='Blank Carbon copy message recipients')
    original_mail_message_id = fields.Char()
    attachment_ids = fields.Many2many(
        'ir.attachment', 'mail_inbox_attachment_rel',
        'mail_id', 'attachment_id',
        string='Attachments')
    attachment_count = fields.Integer('Attachment Count', compute='_compute_attachment_count')
    state = fields.Selection([
        ('draft', 'draft'),
        ('outgoing', 'Outgoing'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('archived', 'Archived'),
        ('trash', 'Trashed'),
        ('exception', 'Delivery Failed'),
        ('cancel', 'Cancelled'),
    ], 'Status', readonly=True, copy=False, default='draft')
    profile_pic = fields.Image("Profile Picture", max_width=128, max_height=128)

    def _compute_body_content(self):
        for mail in self:
            mail.body_content = mail.body_html

    def _search_body_content(self, operator, value):
        return [('body_html', operator, value)]

    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        """We might not have access to all the attachments of the emails.
        Compute the attachments we have access to,
        and the number of attachments we do not have access to.
        """
        IrAttachment = self.env['ir.attachment']
        for mail_sudo in self.sudo():
            mail_sudo.attachment_count = len(mail_sudo.attachment_ids)

    @api.model_create_multi
    def create(self, values_list):
        new_vals_list = []
        for values in values_list:
            email_to = values.get('email_to', '')
            subject = values.get('subject', '')
            email_cc = values.get('email_cc', '')
            email_bcc = values.get('email_bcc', '')
            body_html = values.get('body_html', '')
            body = tools.html_sanitize(body_html)
            if body:
                body.replace(' ', ' ')
                body = self.env['mail.render.mixin']._replace_local_links(body)
            match = re.match(r'"([^"]+)"', email_to)
            email_to_name = ''
            try:
                if match:
                    email_to_name = match.group(1)
                else:
                    email_to_name = email_to.split("@")[0]
            except Exception as e:
                pass
            values['email_to_name'] = email_to_name
            email_values = [email_to, subject, email_cc, email_bcc, body, email_to_name]
            if any(email_values):
                new_vals_list.append(values)
            else:
                continue
        return super(MailInbox, self).create(new_vals_list)

    def write(self, values):
        mark_on_server = self.env.context.get('mark_on_server', False)
        if 'is_read' in values and mark_on_server:
            is_read = values.get('is_read')
            if isinstance(is_read, bool):
                self.mail_change_read_flag(self.original_mail_message_id, is_read)
        result = super(MailInbox, self).write(values)
        return result

    def get_email_uid_by_message_id(self, mail, message_id):
        mail.select("inbox", readonly=False)
        typ, data = mail.search(None, f'HEADER Message-Id "{message_id}"')
        if typ == 'OK':
            email_uids = data[0].split()
            if email_uids:
                return email_uids[0].decode()
        return None

    def mail_change_read_flag(self, message_id, is_read):
        user_email = self.env.user.email
        if not user_email:
            return
        mail_servers = self.env['fetchmail.server'].sudo().search([('user', '=', user_email)])
        for server in mail_servers:
            connection_type = server._get_connection_type()
            imap_server = None
            if connection_type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select("inbox", readonly=False)
                    email_uid = self.get_email_uid_by_message_id(imap_server, message_id)
                    if email_uid:
                        if is_read:
                            imap_server.store(email_uid, '+FLAGS', '\\Seen')
                        else:
                            imap_server.store(email_uid, '-FLAGS', '\\Seen')
                except Exception:
                    _logger.info("Failed to set Seen Flag from mail server %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if imap_server:
                        try:
                            imap_server.close()
                            imap_server.logout()
                        except OSError:
                            _logger.warning('Failed to properly finish imap connection: %s.', server.name, exc_info=True)

    def unlink(self):
        self = self.sudo()
        return super(MailInbox, self).unlink()

    def _check_if_cron_running(self):
        cron_id = self.env.ref('mail.ir_cron_mail_gateway_action')
        if cron_id:
            try:
                self._cr.execute("""SELECT id FROM "%s" WHERE id IN %%s FOR UPDATE NOWAIT""" % cron_id._table, [tuple(cron_id.ids)], log_exceptions=False)
                self._cr.rollback()
                return False
            except psycopg2.OperationalError:
                self._cr.rollback()
                return True

    @api.model
    def fetch_all_emails(self):
        if self.env.context.get('fetchmail_cron_running'):
            return
        cron_running = self._check_if_cron_running()
        if cron_running:
            return
        user_email = self.env.user.email
        if not user_email:
            return
        mail_servers = self.env['fetchmail.server'].sudo().search([('user', '=', user_email)])
        for mail_server in mail_servers:
            mail_server.fetch_mail()

    def email_send(self, attachment_ids, send_now=True):
        try:
            if not self:
                return False
            if attachment_ids:
                self.write({'attachment_ids': [(6, 0, attachment_ids)]})
            if send_now:
                self.send(raise_exception=False)
            return True
        except Exception as ex:
            _logger.info(f"Error sending email: {ex}")
            return False

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None, alias_domain_id=False):
        IrMailServer = self.env['ir.mail_server']
        # Only retrieve recipient followers of the mails if needed
        mails_with_unfollow_link = self.filtered(lambda m: m.body_html and '/mail/unfollow' in m.body_html)
        recipients_follower_status = (
            None if not mails_with_unfollow_link
            else self.env['mail.followers']._get_mail_recipients_follower_status(mails_with_unfollow_link.ids)
        )

        for mail_id in self.ids:
            success_pids = []
            failure_reason = None
            failure_type = None
            processing_pid = None
            mail = None
            try:
                mail = self.browse(mail_id)
                if mail.state != 'outgoing':
                    continue

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write({
                    'state': 'exception',
                    'failure_reason': _('Error without exception. Probably due to sending an email without computed recipients.'),
                })
                # Update notification in a transient exception state to avoid concurrent
                # update in case an email bounces while sending all emails related to current
                # mail record.
                notifs = self.env['mail.notification'].search([
                    ('notification_type', '=', 'email'),
                    ('mail_mail_id', 'in', mail.ids),
                    ('notification_status', 'not in', ('sent', 'canceled'))
                ])
                if notifs:
                    notif_msg = _('Error without exception. Probably due to concurrent access update of notification records. Please see with an administrator.')
                    notifs.sudo().write({
                        'notification_status': 'exception',
                        'failure_type': 'unknown',
                        'failure_reason': notif_msg,
                    })
                    # `test_mail_bounce_during_send`, force immediate update to obtain the lock.
                    # see rev. 56596e5240ef920df14d99087451ce6f06ac6d36
                    notifs.flush_recordset(['notification_status', 'failure_type', 'failure_reason'])

                # protect against ill-formatted email_from when formataddr was used on an already formatted email
                emails_from = tools.email_split_and_format(mail.email_from)
                email_from = emails_from[0] if emails_from else mail.email_from

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                # TDE note: could be great to pre-detect missing to/cc and skip sending it
                # to go directly to failed state update
                email_list = mail._prepare_outgoing_list(recipients_follower_status)

                # send each sub-email
                for email in email_list:
                    # if given, contextualize sending using alias domains
                    if alias_domain_id:
                        alias_domain = self.env['mail.alias.domain'].sudo().browse(alias_domain_id)
                        SendIrMailServer = IrMailServer.with_context(
                            domain_notifications_email=alias_domain.default_from_email,
                            domain_bounce_address=email['headers'].get('Return-Path') or alias_domain.bounce_email,
                        )
                    else:
                        SendIrMailServer = IrMailServer
                    msg = SendIrMailServer.build_email(
                        email_from=email_from,
                        email_to=email['email_to'],
                        subject=email['subject'],
                        body=email['body'],
                        body_alternative=email['body_alternative'],
                        email_cc=tools.email_split(mail.email_cc),
                        email_bcc=tools.email_split(mail.email_bcc),
                        reply_to=email['reply_to'],
                        attachments=email['attachments'],
                        message_id=email['message_id'],
                        references=email['references'],
                        object_id=email['object_id'],
                        subtype='html',
                        subtype_alternative='plain',
                        headers=email['headers'],
                    )
                    processing_pid = email.pop("partner_id", None)
                    try:
                        res = SendIrMailServer.send_email(
                            msg, mail_server_id=mail.mail_server_id.id, smtp_session=smtp_session)
                        if processing_pid:
                            success_pids.append(processing_pid)
                        processing_pid = None
                    except AssertionError as error:
                        if str(error) == IrMailServer.NO_VALID_RECIPIENT:
                            # if we have a list of void emails for email_list -> email missing, otherwise generic email failure
                            if not email.get('email_to') and failure_type != "mail_email_invalid":
                                failure_type = "mail_email_missing"
                            else:
                                failure_type = "mail_email_invalid"
                            # No valid recipient found for this particular
                            # mail item -> ignore error to avoid blocking
                            # delivery to next recipients, if any. If this is
                            # the only recipient, the mail will show as failed.
                            _logger.info("Ignoring invalid recipients for mail.mail %s: %s",
                                         mail.message_id, email.get('email_to'))
                        else:
                            raise
                if res:  # mail has been sent at least once, no major exception occurred
                    mail.write({'state': 'sent', 'message_id': res, 'failure_reason': False})
                    _logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
                    # /!\ can't use mail.state here, as mail.refresh() will cause an error
                    # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                mail._postprocess_sent_message(success_pids=success_pids, failure_type=failure_type)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception(
                    'MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option',
                    mail.id, mail.message_id)
                # mail status will stay on ongoing since transaction will be rollback
                raise
            except (psycopg2.Error, smtplib.SMTPServerDisconnected):
                # If an error with the database or SMTP session occurs, chances are that the cursor
                # or SMTP session are unusable, causing further errors when trying to save the state.
                _logger.exception(
                    'Exception while processing mail with ID %r and Msg-Id %r.',
                    mail.id, mail.message_id)
                raise
            except Exception as e:
                if isinstance(e, AssertionError):
                    # Handle assert raised in IrMailServer to try to catch notably from-specific errors.
                    # Note that assert may raise several args, a generic error string then a specific
                    # message for logging in failure type
                    error_code = e.args[0]
                    if len(e.args) > 1 and error_code == IrMailServer.NO_VALID_FROM:
                        # log failing email in additional arguments message
                        failure_reason = tools.ustr(e.args[1])
                    else:
                        failure_reason = error_code
                    if error_code == IrMailServer.NO_VALID_FROM:
                        failure_type = "mail_from_invalid"
                    elif error_code in (IrMailServer.NO_FOUND_FROM, IrMailServer.NO_FOUND_SMTP_FROM):
                        failure_type = "mail_from_missing"
                # generic (unknown) error as fallback
                if not failure_reason:
                    failure_reason = tools.ustr(e)
                if not failure_type:
                    failure_type = "unknown"

                _logger.exception('failed sending mail (id: %s) due to %s', mail.id, failure_reason)
                mail.write({
                    "failure_reason": failure_reason,
                    "failure_type": failure_type,
                    "state": "exception",
                })
                mail._postprocess_sent_message(
                    success_pids=success_pids,
                    failure_reason=failure_reason, failure_type=failure_type
                )
                if raise_exception:
                    if isinstance(e, (AssertionError, UnicodeEncodeError)):
                        if isinstance(e, UnicodeEncodeError):
                            value = "Invalid text: %s" % e.object
                        else:
                            value = '. '.join(e.args)
                        raise MailDeliveryException(value)
                    raise

            if auto_commit is True:
                self._cr.commit()
        return True
