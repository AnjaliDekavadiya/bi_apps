from odoo import models, fields, api, _
import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import html


class KsMailMessage(models.Model):
    _inherit = 'mail.message'

    ks_cc = fields.Char("Ks Sent Mail Recipients", default=False)
    ks_bcc = fields.Char("Ks Sent Mail cc", default=False)
    ks_send_to = fields.Char("Ks Sent Mail bcc", default=False)
    ks_sent_from = fields.Char(default=False)
    ks_user_id = fields.Many2one("res.users", default=False)


class KsMailsUsers(models.Model):
    """ This Class is Inherited
        This Class will handle the syncing process."""

    _inherit = 'res.users'

    ks_import_office365_mail = fields.Boolean(string="Import Mails", default=True, readonly=True)
    ks_export_office365_mail = fields.Boolean(string="Export Mails", default=True, readonly=True)
    ks_sync_using_date = fields.Boolean(string='Date & Time:', readonly=True, default=True)
    ks_sync_using_email = fields.Boolean(string="Sender's Email:", readonly=True, default=True)
    ks_sync_using_mail_subject = fields.Boolean(string='Subject:', readonly=True, default=True)
    ks_sync_days_before = fields.Integer(string="Sync mails from last (In Days)", default=1,
                                         help="This will allow you to sync only those contacts that are created or "
                                              "updated in the given days. Here 0 days means Today.")
    ks_sync_using_days = fields.Boolean(default=True)
    ks_mail_filter_domain = fields.Char(string="", help="This filter domain is only applicable while syncing from "
                                                        "Odoo to office 365.")
    ks_option_inbox = fields.Boolean(string="Inbox", default=True, help="Using Inbox folder of Outlook")
    ks_option_sentitems = fields.Boolean(string="Sent Items", default=True, help="Using Sentitems folder of Outlook")
    ks_option_archive = fields.Boolean(string="Archive", default=True, help="Using archive folder of Outlook")
    ks_sync_without_attachment = fields.Boolean(string="Sync without attachment (For corrupt attachment)", default=True,
                                                help="If any mail's attachment is corrupt or could not be synced. "
                                                     "Do you still want to create that mail?")

    ks_sync_using_category = fields.Many2many('mail.category', string="Mail category",
                                              help="This will allow you to sync only selected mails")
    ks_is_manager_mail = fields.Boolean("Is Manager", compute="_ks_is_manager_mail", default=False)

    def _ks_is_manager_mail(self):
        for rec in self:
            if self.env.user.has_group("ks_office365_base.office_manager_group_id"):
                rec.ks_is_manager_mail = True
            else:
                rec.ks_is_manager_mail = False

    def ks_is_mail_job_finished(self, ks_mail_job):
        ks_previous_job = self.env["ks.office.mail.job"].search([('ks_mail_status', '=', 'error'),
                                                                 ('ks_mail_module', '=', 'mail'),
                                                                 ('create_uid', '=', self.env.user.id)])
        is_ks_process_running = self.env["ks.office.mail.job"].search([('ks_mail_status', '=', 'in_process'),
                                                                       ('ks_mail_module', '=', 'mail'),
                                                                       ('create_uid', '=', self.id)])

        if is_ks_process_running:
            return False
        elif ks_previous_job and ks_previous_job[0].ks_mail_job == ks_mail_job:
            return ks_previous_job[0]
        else:
            return self.env["ks.office.mail.job"].create({'ks_mail_status': 'in_process', 'ks_mail_module': 'mail',
                                                          'ks_mail_job': ks_mail_job})

    def ks_get_mails(self):
        """This Function Fetches the Mails from the Office 365
            And Update the Local Database. """
        try:
            if self.ks_sync_using_days:
                _days = str(self.ks_sync_days_before)
                if not (_days.isdigit() and not len(_days) > 3) or int(_days) < 0:
                    return self.ks_show_error_message(_("Days can only be in numbers less"
                                                        "than 999 and greater than or equal 0."))
            ks_res = self._ks_get_mails()
            return ks_res
        except Exception as ex:
            if type(ex) is requests.exceptions.ConnectionError:
                ex = "Internet Connection Failed"
            self.env.cr.commit()
            ks_current_job = self.env["ks.office.mail.job"].search([('ks_mail_status', '=', 'in_process'),
                                                                    ('ks_mail_job', '=', 'mail_import'),
                                                                    ('create_uid', '=', self.env.user.id)])
            if ks_current_job:
                ks_current_job.write({'ks_mail_status': 'error', 'ks_mail_error_text': ex})
            self.ks_create_log("authentication", "Authentication", "", 0, datetime.today(), "office_to_odoo",
                               "authentication", "failed", str(ex) +
                               _("\nCheck Jobs to know how many records have been processed."))
            return self.ks_has_mail_sync_error()

    def _ks_get_mails(self):
        """This Function Checks The Authentication Process And
                Pending Job Related To Mail Syncing Activity. """

        ks_current_datetime = datetime.today()
        ks_sync_mail_from_date = datetime.min.date().replace(year=1900)
        if self.ks_sync_using_days:
            ks_days = self.ks_sync_days_before
            ks_sync_mail_from_date = ks_current_datetime.date() + relativedelta(days=-ks_days)

        ks_auth_token = self.env["res.users"].search(
            [("id", "=", self.id)]).ks_auth_token
        if not ks_auth_token:
            self.ks_create_log("authentication", "Authentication", "", 0, ks_current_datetime, "office_to_odoo",
                               "authentication", "failed", _("Generate Authentication Token"))
            return self.ks_show_error_message(_("Generate Authentication Token"))

        ks_folder_list = self.ks_get_folders_list()
        if not ks_folder_list:
            return self.ks_show_error_message(_("Please Select at Least one mail folder to sync"))
        # Checks If Syncing Private Mail Channels Are Exists
        self.ks_check_mail_channel_exits()
        ks_current_job = self.ks_is_mail_job_finished(ks_mail_job="mail_import")
        if not ks_current_job:
            return self.ks_show_error_message(_('Process Is Already Running.'))
        else:
            ks_current_job.write({'ks_mail_status': 'in_process', 'ks_mail_error_text': False})

        head = {
            "Authorization": ks_auth_token,
            "Host": "graph.microsoft.com"
        }

        ks_sync_error = False
        ks_inbox_mail_count_imported = ks_current_job.ks_inbox_records
        ks_sent_mail_count_imported = ks_current_job.ks_sentbox_records
        ks_archive_mail_count_imported = ks_current_job.ks_archive_records
        ks_current_datetime = datetime.today()
        mails = []
        for folder in ks_folder_list:
            ks_api_endpoint = self.ks_make_endpoint(ks_inbox_mail_count_imported, ks_sent_mail_count_imported,
                                                    ks_archive_mail_count_imported,
                                                    folder, ks_sync_mail_from_date, None, top=1, )
            ks_response = requests.get(ks_api_endpoint, headers=head)
            ks_json_data = json.loads(ks_response.text)
            if 'error' in ks_json_data:
                if ks_json_data["error"]['code'] == 'InvalidAuthenticationToken':
                    self.refresh_token()
                    head['Authorization'] = self.ks_auth_token
                    ks_response = requests.get(ks_api_endpoint, headers=head)
                    ks_json_data = json.loads(ks_response.text)
                else:
                    self.ks_create_log("authentication", "Authentication", "", 0, datetime.today(),
                                       "office_to_odoo", "authentication", "failed",
                                       _(ks_json_data["error"]['code']))
                    ks_current_job.write({'ks_mail_status': 'completed'})
                    return self.ks_show_error_message(_("Some error occurred! \nPlease check logs for more "
                                                        "information."))
            # Running the Loop when the data is too much
            while True:
                mails.extend(ks_json_data['value'])
                emails = ks_json_data['value']
                if '@odata.nextLink' in ks_json_data:
                    # Fetches the next bunch of Emails From The Server.
                    new_endpoint = ks_json_data['@odata.nextLink']
                    new_response = requests.get(new_endpoint, headers=head)
                    ks_json_data = json.loads(new_response.text)
                    if 'value' in ks_json_data:
                        emails.extend(ks_json_data['value'])
                    elif 'error' in ks_json_data:
                        self.ks_create_log("authentication", "Authentication", "", 0, ks_current_datetime,
                                           "office_to_odoo", "authentication", "failed",
                                           _(ks_json_data["error"]['code']))
                        return self.ks_show_error_message(_("Some error occurred! \nPlease check logs for "
                                                            "more information."))
                else:
                    break
            ks_sync_error = False
            emails.reverse()
            for mail in emails:
                check = 1
                if self.ks_sync_using_category:
                    check = 0
                    categories = [x.casefold() for x in mail['categories']]
                    for cat in self.ks_sync_using_category:
                        if cat.name.casefold() in categories:
                            check = 1
                if check:
                    ks_exists = self.ks_check_exist(mail, folder)
                    ks_some_error = False
                    if not ks_exists:
                        ks_some_error = self.ks_create_message(mail, head, folder)
                        if ks_some_error:
                            ks_sync_error = True
                    # else:
                    #     ks_body = mail.get('body').get('content')
                    #     if ks_body:
                    #         ks_is_inline = self.ks_check_inline_attachment(ks_body)
                    #         ks_refresh_body = self.ks_reformat_mail_body(ks_body)
                    #     else:
                    #         ks_is_inline = False
                    #         ks_refresh_body = ks_body
                    #     if mail.get('hasAttachments') or ks_is_inline:
                    #         for attachment in ks_json_data.get('value'):
                    #             attachment_id = attachment.get('id')
                    #             if attachment['contentBytes']:
                    #                 data_attach = self.env['ir.attachment'].search([(
                    #                     'name', '=', attachment.get('name'),
                    #                     'datas', '=', attachment.get('contentBytes').encode('utf-8'),
                    #                     'store_fname', '=', attachment.get('name'),
                    #                     'description', '=', attachment.get('name'),
                    #                     'res_model', '=', 'mail.channel',
                    #                     'mimetype', '=', attachment.get('contentType'),
                    #                 )])
                    #                 if not data_attach:
                    #                     data_attach = {
                    #                         'name': attachment.get('name'),
                    #                         'datas': attachment.get('contentBytes').encode('utf-8'),
                    #                         'type': 'binary',
                    #                         'store_fname': attachment.get('name'),
                    #                         'description': attachment.get('name'),
                    #                         'res_model': 'mail.channel',
                    #                         'mimetype': attachment.get('contentType'),
                    #                     }
                    #                     ks_attach_res_id = self.env['ir.attachment'].create(data_attach)
                    if ks_exists or not ks_some_error:
                        if folder == 'archive':
                            ks_archive_mail_count_imported += 1
                            ks_current_job.write({'ks_archive_records': ks_archive_mail_count_imported})
                        elif folder == 'inbox':
                            ks_inbox_mail_count_imported += 1
                            ks_current_job.write({'ks_inbox_records': ks_inbox_mail_count_imported})
                        else:
                            ks_sent_mail_count_imported += 1
                            ks_current_job.write({'ks_sentbox_records': ks_sent_mail_count_imported})
        if not ks_sync_error:
            # Completing The Process Without Error.
            ks_current_job.write({'ks_mail_status': 'completed'})
            return self.ks_no_mail_sync_error()
        else:
            # Completing The Process with Error.
            ks_current_job.write({'ks_mail_status': 'completed'})
            return self.ks_has_mail_sync_error()

    def ks_get_folders_list(self):
        ks_folder_list = list()
        if self.ks_option_archive:
            ks_folder_list.append('archive')
        if self.ks_option_inbox:
            ks_folder_list.append('inbox')
        if self.ks_option_sentitems:
            ks_folder_list.append('sentitems')
        if not ks_folder_list:
            return False
        return ks_folder_list

    def ks_create_message(self, mail_data, head, folder):
        """ This Function will Create the mail.message for every Incoming Email """
        ks_some_error = False

        ks_subject = mail_data.get('subject')
        ks_body = mail_data.get('body').get('content')
        if mail_data.get('sender'):
            ks_email_from = mail_data.get('sender').get('emailAddress').get('address')
        else:
            ks_email_from = " "
        if ks_body:
            ks_is_inline = self.ks_check_inline_attachment(ks_body)
            ks_refresh_body = self.ks_reformat_mail_body(ks_body)
        else:
            ks_is_inline = False
            ks_refresh_body = ks_body

        log_rec_name = "FROM: %s, SUBJECT: %s" % (ks_email_from, ks_subject or "[No Subject]")

        ks_attachment_error = False
        ks_attachment_ids = list()
        if mail_data.get('hasAttachments') or ks_is_inline:
            ks_inbox_mail_count_imported = 0
            ks_sent_mail_count_imported = 0
            ks_archive_mail_count_imported = 0
            ks_attach_id = str(mail_data.get('id'))
            ks_api_endpoint = self.ks_make_endpoint(ks_inbox_mail_count_imported, ks_sent_mail_count_imported,
                                                    ks_archive_mail_count_imported, folder_name=folder, ks_sync_date=0,
                                                    ks_attachment=ks_attach_id, top=0)
            ks_response = requests.get(ks_api_endpoint, headers=head)
            ks_json_data = json.loads(ks_response.text)
            if 'error' in ks_json_data:
                self.ks_create_log("mail", "Error", "", 0, datetime.today(), "office_to_odoo", False, "failed",
                                   _(ks_json_data["error"]['code']))
                return True

            for attachment in ks_json_data.get('value'):
                attachment_id = attachment.get('id')
                if attachment['contentBytes']:
                    try:
                        data_attach = {
                            'name': attachment.get('name'),
                            'datas': attachment.get('contentBytes').encode('utf-8'),
                            'type': 'binary',
                            'store_fname': attachment.get('name'),
                            'description': attachment.get('name'),
                            'res_model': 'discuss.channel',
                            'mimetype': attachment.get('contentType'),
                        }
                        ks_attach_res_id = self.env['ir.attachment'].create(data_attach)
                        ks_attachment_ids.append(ks_attach_res_id.id)
                    except Exception as ex:
                        ks_attachment_error = True
                else:
                    ks_attachment_error = True

        ks_date = mail_data.get('receivedDateTime')
        ks_date = ks_date.split('T')[0] + ' ' + ks_date.split('T')[1][:-1]

        ks_message_id = mail_data.get('internetMessageId')
        ks_author_id = self.partner_id.id

        if not ks_attachment_error or self.ks_sync_without_attachment:
            try:
                ks_channel_id = None
                if folder == 'inbox':
                    # ks_channel_id = [(4, channel.id) for channel in self.ks_office365_channel_inbox]
                    ks_channel_id = self.ks_office365_channel_inbox
                if folder == 'sentitems':
                    # ks_channel_id = [(4, channel.id) for channel in self.ks_office365_channel_sentitems]
                    ks_channel_id = self.ks_office365_channel_sentitems
                if folder == 'archive':
                    # ks_channel_id = [(4, channel.id) for channel in self.ks_office365_channel_archive]
                    ks_channel_id = self.ks_office365_channel_archive
                ks_recipient = mail_data.get('toRecipients')
                if ks_recipient and folder == 'sentitems':
                    ks_partners = self.ks_check_partner(ks_recipient)
                else:
                    ks_partners = [(4, self.partner_id.id)]

                ks_send_to, ks_sent_from, ks_cc, ks_bcc = str(), str(), str(), str()
                ks_sent_from = mail_data['sender']['emailAddress']['address']
                for rec in mail_data['toRecipients']:
                    ks_send_to += rec['emailAddress']['address'] + ', '
                ks_send_to = ks_send_to[:-2]
                for cc in mail_data['ccRecipients']:
                    ks_cc += cc['emailAddress']['address'] + ', '
                ks_cc = ks_cc[:-2]
                for bcc in mail_data['bccRecipients']:
                    ks_bcc += bcc['emailAddress']['address'] + ', '
                ks_bcc = ks_bcc[:-2]

                data = {
                    'subject': ks_subject or '[No Subject]',
                    'date': ks_date,
                    'body': ks_refresh_body,
                    'message_type': 'email',
                    'subtype_id': 1,
                    'model': 'discuss.channel',
                    'res_id': ks_channel_id.id if ks_channel_id else False,
                    'email_from': ks_email_from,
                    'author_id': ks_author_id,
                    'partner_ids': ks_partners,
                    # 'needaction_partner_ids': [(4, ks_author_id)],
                    'message_id': ks_message_id,
                    'ks_sent_from': ks_sent_from,
                    'ks_send_to': ks_send_to,
                    'ks_user_id': self.id,
                    'ks_bcc': ks_bcc,
                    'ks_cc': ks_cc,
                }
                if len(data['body'].split('>')) == 11 and len(data['body'].split('>')[10].split('<')[0]) < 1:
                    body = data['body'].replace('<br>', 'No Body')
                    body.replace('<br>', 'No Body')
                    data.update({'body': body})
                res = self.env['mail.message'].sudo().create(data)
                res.sudo().write({'attachment_ids': [(4, aid) for aid in ks_attachment_ids]})

                log_msg = "Mail synced!" if not ks_attachment_error else "Mail synced but some attachment could " \
                                                                         "not be created."
                self.ks_create_log("mail", log_rec_name, ks_message_id, ks_author_id, datetime.today(),
                                   "office_to_odoo", "create", "success", _(log_msg))
            except Exception as ex:
                self.ks_create_log("mail", log_rec_name, ks_message_id, ks_author_id, datetime.today(),
                                   "office_to_odoo",
                                   "create", "failed", _("Record is not created created! \nReason: " + str(ex)))
                ks_some_error = True
        else:
            self.ks_create_log("mail", log_rec_name, ks_message_id, ks_author_id, datetime.today(), "office_to_odoo",
                               "create", "failed",
                               _("Mail is not synced because some attachment could not be created!"))
            ks_some_error = True

        return ks_some_error

    def ks_check_exist(self, mail, folder):
        """This Function Checks if the Mails are already in system."""

        ks_mail_folder = {
            'inbox': self.ks_office365_channel_inbox.id,
            'sentitems': self.ks_office365_channel_sentitems.id,
            'archive': self.ks_office365_channel_archive.id,
        }

        if mail.get('internetMessageId'):
            ks_mail = self.env['mail.message'].sudo().search([('message_id', '=', mail.get('internetMessageId')),
                                                              ('ks_user_id', '=', self.id)])
            if ks_mail:
                # if not ks_mail.channel_ids:
                #     self.env.cr.execute(
                #         "select mail_channel_id from mail_message_mail_channel_rel where mail_message_id = %(id)s",
                #         {'id': ks_mail.id})
                #
                #     mail_channel_ids = [id[0] for id in self.env.cr.fetchall()]
                # else:
                #     mail_channel_ids = ks_mail.channel_ids.ids

                # Check if message don't have the channel then assign.
                if ks_mail.res_id or ks_mail.model:
                    self.env.cr.execute("""
                        UPDATE mail_message
                        SET res_id = %s, model = 'discuss.channel'
                        WHERE id = %s
                    """, (ks_mail_folder[folder], ks_mail.id))

                log_name = "Subject: " + (mail.get('subject') or "<No Subject>") + " / From: " + \
                           mail.get('sender').get('emailAddress').get('address')
                # if folder == 'archive':
                #     self.env.cr.execute("delete from mail_message_mail_channel_rel where mail_message_id = %(id)s",
                #                         {'id': ks_mail.id})
                #     if ks_mail_folder[folder]:
                #         self.env.cr.execute("INSERT INTO mail_message_mail_channel_rel(mail_message_id, mail_channel_id)"
                #                             "VALUES (%(m_id)s, %(c_id)s)", {'m_id': ks_mail.id,
                #                                                             'c_id': ks_mail_folder[folder]})
                #
                # elif ks_mail_folder[folder] not in mail_channel_ids:
                #     if ks_mail_folder[folder]:
                #         self.env.cr.execute("INSERT INTO mail_message_mail_channel_rel(mail_message_id, mail_channel_id)"
                #                             "VALUES (%(m_id)s, %(c_id)s)", {'m_id': ks_mail.id,
                #                                                             'c_id': ks_mail_folder[folder]})
                self.ks_create_log("mail", log_name, mail.get('internetMessageId'), self.partner_id.id,
                                   datetime.today(), "office_to_odoo", "update", "success",
                                   _("Mail moved to %s channel" % folder))
                return True
            else:
                return False
        else:
            return True

    def ks_check_inline_attachment(self, ks_mail_body):
        """ This Function Checks Whether Images Are Stored As Inline Image."""
        try:
            root = html.fromstring(ks_mail_body)
        except ValueError:
            # In case the email client sent XHTML, fromstring will fail because 'Unicode strings
            # with encoding declaration are not supported'.
            root = html.fromstring(ks_mail_body.encode('utf-8'))
        ks_image_tag = [node for node in root.iter()
                        if node.tag == 'img' and
                        node.get('src', '').startswith('cid:')]
        if len(ks_image_tag):
            return True
        else:
            return False

    def ks_reformat_mail_body(self, mail_body):
        """ This Function will Remove the
            Image Residuals From the Mail Body"""
        try:
            root = html.fromstring(mail_body)
        except ValueError:
            root = html.fromstring(mail_body.encode('utf-8'))
        ks_image_tag = [node for node in root.iter()
                        if node.tag == 'img' and
                        node.get('src', '').startswith('cid:')]
        # If Image Tags are Present, Their Html tags are Removed From The Body.
        # And Decoding the Body Again in string Form for Storage.
        if len(ks_image_tag):
            for node in ks_image_tag:
                node.getparent().remove(node)
            return html.tostring(root).decode('utf-8')
        else:
            return mail_body

    def ks_refresh_authentication_token(self, ks_json_data, ks_api_endpoint, ks_current_datetime, head):
        """This Function Will Re-Generate The Authentication Token"""

        if ks_json_data["error"]['code'] == 'InvalidAuthenticationToken':
            self.refresh_token()
            head['Authorization'] = self.ks_auth_token
            ks_response = requests.get(ks_api_endpoint, headers=head)
            ks_json_data = json.loads(ks_response.text)
            if 'error' in ks_json_data:
                self.ks_create_log("authentication", "Authentication", "",
                                   0, ks_current_datetime, "office_to_odoo",
                                   "authentication", "failed",
                                   ks_json_data["error"]['code'])
                return self.ks_show_error_message(_("Some error occurred! \nPlease "
                                                    "check logs for more information."))
            return ks_response.status_code
        else:
            self.ks_create_log("authentication", "Authentication", "", 0,
                               ks_current_datetime, "office_to_odoo",
                               "authentication", "failed",
                               ks_json_data["error"]['code'])
            return self.ks_show_error_message(_("Some error occurred! \nPlease "
                                                "check logs for more information."))

    # def ks_post_mails(self):
    #     """This Function Fetches the Mails from the Office 365
    #         And Update the Local Database. """
    #     try:
    #         if self.ks_sync_using_days:
    #             _days = str(self.ks_sync_days_before)
    #             if not (_days.isdigit() and not len(_days) > 3) or int(_days) < 0:
    #                 return self.ks_show_error_message(_("Days can only be in numbers less "
    #                                                     "than 999 and greater than or equal 0."))
    #         ks_res = self._ks_post_mails()
    #         return ks_res
    #     except Exception as ex:
    #         if type(ex) is requests.exceptions.ConnectionError:
    #             ex = "Internet Connection Failed"
    #         self.env.cr.commit()
    #         ks_current_job = self.env["ks.office.job"].sudo()\
    #                              .search([('ks_records', '>=', 0),
    #                                       ('ks_status', '=', 'in_process'),
    #                                       ('ks_job', '=', 'mail_export'),
    #                                       ('create_uid', '=', self.env.user.id)])
    #         if ks_current_job:
    #             ks_current_job.write({'ks_status': 'error', 'ks_error_text': ex})
    #         self.ks_create_log("authentication", "Authentication", "", 0,
    #                            datetime.today(), "odoo_to_office",
    #                            "authentication", "failed", str(ex) +
    #                            "\nCheck Jobs to know how many records have been processed.")
    #         return self.ks_has_mail_sync_error()

    # def _ks_post_mails(self):
    #     """This Function will create the mail message to the Office 365 Repository"""
    #
    #     ks_current_job = self.sudo().ks_is_mail_job_finished(ks_job="mail_export")
    #     if not ks_current_job:
    #         return self.ks_show_error_message(_('Process Is Already Running.'))
    #     else:
    #         ks_current_job.write({'ks_status': 'in_process', 'ks_error_text': False})
    #
    #     ks_current_datetime = datetime.today()
    #     ks_sync_mail_from_date = datetime.min.date().replace(year=1900)
    #     if self.ks_sync_using_days:
    #         ks_days = self.ks_sync_days_before
    #         ks_sync_mail_from_date = ks_current_datetime.date() + relativedelta(days=-ks_days)
    #
    #     ks_auth_token = self.env["res.users"].sudo().search(
    #                             [("id", "=", self.id)]).ks_auth_token
    #     if not ks_auth_token:
    #         self.ks_create_log("authentication", "Authentication", "",
    #                            0, ks_current_datetime, "odoo_to_office",
    #                            "authentication", "failed",
    #                            "Generate Authentication Token")
    #         return self.ks_show_error_message(_("Generate Authentication Token"))
    #
    #     head = {
    #         "Authorization": ks_auth_token,
    #         "Host": "graph.microsoft.com"
    #     }
    #     ks_mail_exported = ks_current_job.ks_records
    #     # Incoming Mails and Outgoing Mails Are Posted into the
    #     # Sentitems folder and Inbox depending upon Receiver or Sender.
    #     destination_folders = ['sentitems', 'Inbox']
    #     ks_sync_error = False
    #     ks_mail_exported = 0
    #     ks_mail_count_exported = 0
    #     for destination_folder in destination_folders:
    #         ks_mail_search_domain = self.ks_get_mail_search_domain(self.ks_mail_filter_domain,
    #                                                                ks_sync_mail_from_date)
    #         if destination_folder == 'sentitems':
    #             ks_folder_list = ['sentitems', 'archive']
    #             ks_mail_mail_domain = ks_mail_search_domain + [('author_id', '=', self.partner_id.id)]
    #         else:
    #             ks_folder_list = ['Inbox', 'archive']
    #             ks_mail_mail_domain = ks_mail_search_domain + [('recipient_ids', 'in', self.partner_id.id)]
    #         mails = []
    #         for folder in ks_folder_list:
    #             ks_api_endpoint = self.ks_make_endpoint(ks_mail_exported,
    #                                                     folder_name=folder,
    #                                                     ks_sync_date=ks_sync_mail_from_date,
    #                                                     ks_attachment="",
    #                                                     top=1)
    #             ks_response = requests.get(ks_api_endpoint, headers=head)
    #             ks_json_data = json.loads(ks_response.text)
    #             if 'error' in ks_json_data:
    #                 ks_status_code = self.ks_refresh_authentication_token(ks_json_data,
    #                                                                       ks_api_endpoint,
    #                                                                       ks_current_datetime,
    #                                                                       head)
    #                 if ks_status_code == 200:
    #                     ks_api_endpoint = self.ks_make_endpoint(ks_mail_exported,
    #                                                             folder_name=folder,
    #                                                             ks_sync_date=ks_sync_mail_from_date,
    #                                                             ks_attachment="",
    #                                                             top=1)
    #                     ks_response = requests.get(ks_api_endpoint, headers=head)
    #                     ks_json_data = json.loads(ks_response.text)
    #                 else:
    #                     self.ks_create_log("authentication", "Authentication", "",
    #                                        0, ks_current_datetime, "odoo_to_office",
    #                                        "authentication", "failed",
    #                                        ks_json_data["error"]['code'])
    #                     return self.ks_has_mail_sync_error()
    #
    #             mails.extend(ks_json_data['value'])
    #         ks_sync_error = False
    #         users_mail = self.env['mail.mail'].search(ks_mail_mail_domain)
    #         for odoo_mail in users_mail:
    #             ks_mail = self.ks_match_message(odoo_mail, mails)
    #             ks_folder = destination_folder
    #             if not ks_mail:
    #                 ks_some_error = self.ks_create_mail_data(odoo_mail, ks_folder, ks_mail_exported, head)
    #                 if ks_some_error:
    #                     ks_sync_error = True
    #                 else:
    #                     ks_mail_count_exported += 1
    #                     ks_current_job.write({'ks_records': ks_mail_count_exported})
    #
    #     if not ks_sync_error:
    #         ks_current_job.write({'ks_status': 'completed', 'ks_records': ks_mail_count_exported})
    #         return self.ks_no_mail_sync_error()
    #     else:
    #         ks_current_job.write({'ks_status': 'completed', 'ks_records': ks_mail_count_exported})
    #         return self.ks_has_mail_sync_error()

    # def ks_create_mail_data(self, ks_mail_info, folder, ks_mail_exported, head):
    #     """ This Function create the data for email to be Posted into
    #             Sent items and Inbox folder of outlook Account """
    #
    #     if folder == 'sentitems':
    #         ks_mail_data = \
    #             {
    #                 'subject': str(ks_mail_info.subject),
    #                 'importance': "Normal",
    #                 'body':
    #                     {
    #                         "contentType": "html",
    #                         "content":  ks_mail_info.body,
    #                     },
    #                 'toRecipients':
    #                     [
    #                          {
    #                              'emailAddress':
    #                                  {
    #                                      'address': to.email,
    #                                      'name': to.email_formatted,
    #                                   }
    #                           }
    #                         for to in ks_mail_info.recipient_ids
    #                     ],
    #                 'sender':
    #                     {
    #                         'emailAddress':
    #                             {
    #                                 'address': self.partner_id.email,
    #                                 'name': self.partner_id.name,
    #                             }
    #                     },
    #                 'internetMessageId': str(ks_mail_info.message_id),
    #             }
    #     if folder == 'Inbox':
    #         ks_mail_data = \
    #             {
    #                 'subject': ks_mail_info.subject,
    #                 'importance': "Normal",
    #                 'body':
    #                     {
    #                         "contentType": "html",
    #                         "content":  ks_mail_info.body,
    #                     },
    #                 # 'toRecipients':
    #                 #          {
    #                 #              'emailAddress':
    #                 #                  {
    #                 #                      'address': self.partner_id.email,
    #                 #                      'name': self.partner_id.name,
    #                 #                   }
    #                 #           },
    #                 'sender':
    #                     {
    #                         'emailAddress':
    #                             {
    #                                 'address': ks_mail_info.author_id.email,
    #                                 'name': ks_mail_info.email_from,
    #                             }
    #                     },
    #                 'internetMessageId': str(ks_mail_info.message_id),
    #                 'isDraft': False,
    #             }
    #     ks_api_endpoint = self.ks_make_endpoint(ks_mail_exported,
    #                                             folder_name=folder,
    #                                             ks_sync_date=0,
    #                                             ks_attachment="",
    #                                             top=0)
    #     # Posting The Mail into the outlook server.
    #     ks_response = requests.post(ks_api_endpoint,
    #                                 headers=head,
    #                                 json=ks_mail_data)
    #     ks_json_data = json.loads(ks_response.text)
    #     if 'error' in ks_json_data:
    #         if 'code' in ks_json_data['error']:
    #             ks_error = ks_json_data['error']['code'] + "\n" + ks_json_data['error']['message']
    #         else:
    #             ks_error = ks_json_data['error']['message']
    #         self.ks_create_log("mail", ks_mail_info.email_from + "/" + ks_mail_info.subject,
    #                            ks_json_data.get('internetMessageId'),
    #                            ks_mail_info.id,
    #                            datetime.today(), "odoo_to_office", "create",
    #                            "failed", ks_error)
    #         ks_some_error = True
    #         return ks_some_error
    #     else:
    #         self.ks_create_log("mail", ks_mail_info.email_from + "/" + ks_mail_info.subject,
    #                            ks_json_data.get('internetMessageId'),
    #                            ks_mail_info.id, datetime.today(),
    #                            "odoo_to_office",
    #                            "create", "success", "Record Created At Outlook!")
    #     if ks_mail_info.attachment_ids:
    #         # Posting the Attachment Present Inside the Mail body into the Outlook Server.
    #         ks_api_endpoint = self.ks_make_endpoint(ks_mail_exported,
    #                                                 folder_name=folder,
    #                                                 ks_sync_date=0,
    #                                                 ks_attachment=str(ks_json_data.get('id')),
    #                                                 top=0)
    #         for attach in ks_mail_info.attachment_ids.sudo():
    #             ks_attach_data = {
    #                                     '@odata.type': "#microsoft.graph.fileAttachment",
    #                                     'name': attach.name,
    #                                     'contentBytes': attach.datas.decode('utf-8'),
    #                                     'contentType': 'application/pdf',
    #                                 }
    #             ks_response = requests.post(ks_api_endpoint,
    #                                         headers=head,
    #                                         json=ks_attach_data)
    #             ks_json_data = json.loads(ks_response.text)
    #             ks_some_error = False
    #             if 'error' in ks_json_data:
    #                 self.ks_create_log("mail", attach.name,
    #                                    str(ks_json_data.get('id')),
    #                                    attach.id,
    #                                    datetime.today(), "odoo_to_office", "create", "failed",
    #                                    ks_json_data['error']['message'])
    #                 ks_some_error = True
    #                 return ks_some_error
    #             else:
    #                 self.ks_create_log("mail", attach.name,
    #                                    str(ks_json_data.get('id')),
    #                                    attach.id, datetime.today(),
    #                                    "odoo_to_office",
    #                                    "create", "success", "Attachment Uploaded At Outlook!")

    # def ks_match_message(self, odoo_mail, mails):
    #     """ Function To Match If Message Is Already Sent Or Not """
    #
    #     for mail in mails:
    #         if mail.get('internetMessageId') == odoo_mail.message_id:
    #             return True
    #         else:
    #             ks_mail_date = mail.get('receivedDateTime').split('T')[0]
    #             ks_odoo_date = datetime.strftime(odoo_mail.date, '%Y-%m-%d')
    #             try:
    #                 ks_mail_time = int(mail.get('receivedDateTime').split('T')[1][:2])
    #                 ks_odoo_time = int(datetime.strftime(odoo_mail.date, '%H'))
    #             except Exception as ks_err:
    #                 # Commented to avoid creating the extra log
    #                 # self.ks_create_log("mail", odoo_mail.date + "/" + odoo_mail.subject,
    #                 #                    odoo_mail.message_id,
    #                 #                    mail.id,
    #                 #                    datetime.today(), "odoo_to_office", "create",
    #                 #                    "failed", ks_err)
    #                 print(ks_err)
    #                 continue
    #             ks_mail_recipients = sorted([mail.get('emailAddress').get('address') for mail in mail.get('toRecipients')])
    #             ks_odoo_recipients = sorted([mail.email for mail in odoo_mail.recipient_ids])
    #             if mail.get('subject') == odoo_mail.subject \
    #                     and ks_mail_date == ks_odoo_date\
    #                     and len(ks_mail_recipients) == len(ks_odoo_recipients)\
    #                     and ks_mail_recipients == ks_odoo_recipients\
    #                     and ks_mail_time == ks_odoo_time:
    #                 return True
    #     # If No Matching Result Found, Return False
    #     return False

    def ks_make_endpoint(self, ks_inbox_mail, ks_sent_mail, ks_archive_mail, folder_name, ks_sync_date, ks_attachment,
                         top):
        """This Function Formats the Url to Hit the Server As per the desired folder.
           The below link is assumed constant for all Mail Folders and remains same for Attachments Also"""
        default = 0
        check = 1
        ks_string = "https://graph.microsoft.com/v1.0/me/mailFolders/"
        ks_api_endpoint = ks_string + str(folder_name) + "/messages/"
        if ks_inbox_mail and folder_name == 'inbox':
            ks_api_endpoint += "?$top=1000000&$skip=" + str(ks_inbox_mail)
            check = 0
        if ks_sent_mail and folder_name == 'sentitems':
            ks_api_endpoint += "?$top=1000000&$skip=" + str(ks_sent_mail)
            check = 0
        if ks_archive_mail and folder_name == 'archive':
            ks_api_endpoint += "?$top=1000000&$skip=" + str(ks_archive_mail)
            check = 0
        if top and check:
            ks_api_endpoint += "?$top=1000000&$skip=" + str(default)
        if ks_sync_date:
            ks_api_endpoint += "&$filter=createdDateTime ge " + str(ks_sync_date)
        if ks_attachment:
            ks_api_endpoint += ks_attachment + "/attachments/"

        return ks_api_endpoint

    # def ks_get_mail_search_domain(self, ks_domain, ks_sync_mail_from_date):
    #     """ This Function Forms The Search Domain. """
    #
    #     ks_search_domain_mails = []
    #     if ks_domain:
    #         for dom in eval(ks_domain):
    #             if type(dom) is list and dom[0] != 'author_id':
    #                 ks_search_domain_mails.append(tuple(dom))
    #
    #     ks_search_domain_mails.append(('date', '>=', ks_sync_mail_from_date))
    #     return ks_search_domain_mails

    def ks_has_mail_sync_error(self):
        return {
            'params': {
                'task': 'notify',
                'message': 'Sync Completed!\n Some Mails could not be synced. \nPlease check log for more information.',
            },
        }

    def ks_no_mail_sync_error(self):
        return {
            'name': 'Office365 logs',
            'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ks_office365.logs',
            'view_id': False,
            'context': self.env.context,
        }

    # def ks_check_mail_channel_exits(self):
    #     """ The Function Checks If the Mail Channel Exists
    #             If Not Exists Than Creates The Same. """
    #
    #     private_channel = [self.ks_office365_channel_inbox,
    #                        self.ks_office365_channel_sentitems,
    #                        self.ks_office365_channel_archive]
    #     for channel in private_channel:
    #         if channel.id:
    #             ks_exists = self.env['mail.channel.partner']\
    #                             .search([('channel_id', '=', channel.id)])
    #             if not ks_exists:
    #                 ks_partner_data = {
    #                     'partner_id': self.partner_id.id,
    #                     'channel_id': channel.id,
    #                 }
    #                 try:
    #                     ks_partner_res = self.env['mail.channel.partner']\
    #                                          .create(ks_partner_data)
    #                     channel.update({
    #                         'channel_last_seen_partner_ids': [(4, ks_partner_res.id)]
    #                     })
    #                     self.ks_create_log("mail", "Mail Channel", "",
    #                                        0, datetime.today(), "office_to_odoo",
    #                                        "create", "success",
    #                                        "Mail Channel has been Updated/Created")
    #                 except Exception:
    #                     self.ks_create_log("mail", "Mail Channel", "",
    #                                        0, datetime.today(), "office_to_odoo",
    #                                        "create", "failed",
    #                                        "Error While Updating/Creating Mail Channel")
    #                     return True

    def ks_check_partner(self, recepients):
        """ This Checks The CC and To Names In res.partner And Create The Same If Any One Not Present."""

        ks_recepients = []
        if recepients:
            for recepient in recepients:
                ks_domain = ['|', ('name', '=', recepient.get('emailAddress').get('name')),
                             ('email', '=', recepient.get('emailAddress').get('address'))]
                ks_exist_user = self.env['res.partner'].search(ks_domain, limit=1)
                if len(ks_exist_user) > 1:
                    ks_domain = [('name', '=', recepient.get('emailAddress').get('name')),
                                 ('email', '=', recepient.get('emailAddress').get('address'))]
                    ks_exist_user = self.env['res.partner'].search(ks_domain, limit=1)
                if ks_exist_user:
                    ks_recepients.extend([(4, ks_exist_user.id)])
        return ks_recepients

    def ks_check_mail_channel_exits(self):
        """ The Function Checks If the Mail Channel Exists
                If Not Exists Than Creates The Same. """

        private_channel = [
            self.ks_office365_channel_archive,
            self.ks_office365_channel_inbox,
            self.ks_office365_channel_sentitems
        ]
        for channel in private_channel:
            if channel.id:
                ks_exists = self.env['discuss.channel.member'] \
                    .search([('channel_id', '=', channel.id)])
                if not ks_exists:
                    ks_partner_data = {
                        'partner_id': self.partner_id.id,
                        'channel_id': channel.id,
                    }
                    try:
                        ks_partner_res = self.env['discuss.channel.member'].create(ks_partner_data)
                        channel.update({
                            'channel_last_seen_partner_ids': [(4, ks_partner_res.id)]
                        })
                        self.ks_create_log("mail", "Mail Channel", "", 0, datetime.today(), "office_to_odoo",
                                           "create", "success", _("Mail Channel has been Updated/Created"))
                    except Exception:
                        self.ks_create_log("mail", "Mail Channel", "", 0, datetime.today(), "office_to_odoo",
                                           "create", "failed", _("Error While Updating/Creating Mail Channel"))
                        return True

        # New Code.
        # Check if private channels are not created.
        if not self.ks_office365_channel_archive or not self.ks_office365_channel_inbox or \
                not self.ks_office365_channel_sentitems:
            self.env.user.ks_create_private_mail_channel()

    def ks_check_mail_folder_change(self, ks_mail_check, folder):
        """This Fucntion Checks if the mail folder is changed or not"""

        ks_original_folder = ks_mail_check.channel_ids.id
        ks_mail_folder = {
            self.ks_office365_channel_inbox.id: 'inbox',
            self.ks_office365_channel_sentitems.id: 'sentitems',
            self.ks_office365_channel_archive.id: 'archive',
        }
        if ks_mail_folder.get(ks_original_folder) == folder:
            return False
        else:
            return True

    def ks_change_mail_channel(self, ks_mail_check, folder):
        """This Function Will Change The Channel i.e. and
                Ultimately change the Folder For End User"""

        ks_mail_folder = {
            'inbox': self.ks_office365_channel_inbox.id,
            'sentitems': self.ks_office365_channel_sentitems.id,
            'archive': self.ks_office365_channel_archive.id,
        }
        ks_new_channel_id = ks_mail_folder.get(folder)
        try:
            ks_res = ks_mail_check.update({
                'channel_ids': [(6, 0, [ks_new_channel_id])]
            })
            self.ks_create_log("mail", "Mail Folder", "", ks_new_channel_id, datetime.today(), "office_to_odoo",
                               "update", "success", _("Message in Mail Folder has been Updated"))
        except Exception:
            self.ks_create_log("mail", "Mail Folder", "", ks_new_channel_id, datetime.today(), "office_to_odoo",
                               "update", "failed", _("Error while moving message in Folder"))
