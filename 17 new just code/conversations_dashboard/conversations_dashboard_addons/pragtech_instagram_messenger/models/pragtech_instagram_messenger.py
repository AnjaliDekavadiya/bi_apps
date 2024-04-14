from odoo import api, fields, models, SUPERUSER_ID, modules, _, http
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
import requests
import re
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    instagram_psid = fields.Char(string="Instagram PSID")


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        """Put in logic here"""
        message_new = super(DiscussChannel, self).message_new(msg_dict, custom_values='whatever vslues are derived from the logic')
        return message_new

    def message_update(self, msg_dict, update_vals=None):
        '''Adds cc email to self.email_cc while trying to keep email as raw as possible but unique'''
        if update_vals is None:
            update_vals = {}
        cc_values = {}
        new_cc = self._mail_cc_sanitized_raw_dict(msg_dict.get('cc'))
        if new_cc:
            old_cc = self._mail_cc_sanitized_raw_dict(self.email_cc)
            new_cc.update(old_cc)
            cc_values['email_cc'] = ", ".join(new_cc.values())
        cc_values.update(update_vals)
        return super(DiscussChannel, self).message_update(msg_dict, cc_values)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, message_type='comment', **kwargs):
        message = super(DiscussChannel, self).message_post(message_type='comment', **kwargs)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not self._context.get('from_odoobot'):
            if kwargs.get('attachment_ids'):
                message.write({"message_type": "comment"})
            if self.channel_type == 'multi_livechat_NAME2':
                # print("sending to instagram.....")
                if self.instagram_recipient_id:
                    if message.attachment_ids:
                        # print("sending attachment")
                        if 'png' in message.attachment_ids.mimetype or 'jpg' in message.attachment_ids.mimetype or 'jpeg' in message.attachment_ids.mimetype or 'image' in message.attachment_ids.mimetype:
                            file_type = 'image'
                        elif 'mp4' in message.attachment_ids.mimetype or '3gp' in message.attachment_ids.mimetype or 'avi' in message.attachment_ids.mimetype or 'video' in message.attachment_ids.mimetype:
                            file_type = 'video'
                        else:
                            file_type = 'file'
                        self.send_instagram_attachment_file(self.instagram_recipient_id, file_type, message.attachment_ids)
                    if message.body:
                        # print("sending text to ", self.instagram_recipient_id)
                        # print(self._channel_last_message_ids())
                        if self._channel_last_message_ids():
                            self.send_instagram_text_message(self.instagram_recipient_id, kwargs, message)
                        else:
                            self.send_instagram_first_message(self.instagram_recipient_id, kwargs, message)
                else:
                    raise ValidationError(" No instagram id defined for this recipient")
        return message

    def convert_email_from_to_name(self, str1):
        result = re.search('"(.*)"', str1)
        return result.group(1)

    def custom_html2plaintext(self, html):
        html = re.sub('<br\s*/?>', '\n', html)
        html = re.sub('<.*?>', ' ', html)
        return html

    def send_instagram_text_message(self, recipient_id, kwargs, message):
        # url format is 'https://graph.facebook.com/v13.0/me/messages?access_token=<PAGE_ACCESS_TOKEN>'
        html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))
        instagram_page_access = self.env['ir.config_parameter'].sudo().get_param('pragtech_instagram_messenger.instagram_page_access')
        if instagram_page_access:
            url = 'https://graph.facebook.com/v12.0/me/messages?access_token={}'.format(instagram_page_access)
            params = {
                "messaging_type": "RESPONSE",
                "recipient": {
                    "id": recipient_id
                },
                "message": {
                    "text": html_to_plain_text
                }
            }

            headers = {'content-type': 'application/json'}

            response = requests.post(url, json=params, headers=headers)
            # print(response.status_code)
            # print(response.content)
            if not response.status_code == 200 or response.status_code == 201:
                raise ValidationError(response.status_code+" message not sent, try again")
        else:
            raise ValidationError("Input your page access token in the configuration")

    def send_instagram_attachment_file(self, recipient_id, file_type, attachment_url):
        instagram_page_access = self.env['ir.config_parameter'].sudo().get_param('pragtech_instagram_messenger.instagram_page_access')
        url = 'https://graph.facebook.com/v12.0/me/messages?access_token={}'.format(instagram_page_access)
        # print(recipient_id)
        # print(file_type)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # print(base_url)
        attachment_data = base64.b64decode(attachment_url.datas)
        recipient = {
                "id": recipient_id
            }
        message = {
            "attachment": {
                "type": 'image',  # audio, video, image or file
                "payload": {
                    "is_reusable": True,
                    'url': base_url+"/instagram/attachments/message?attachment_id={}".format(attachment_url.id)
                }
            }
        }
        # print(json.dumps(message))

        files2 = {
            'recipient': (None, json.dumps(recipient)),
            'message': (None, json.dumps(message), 'application/json'),
            'filedata': (attachment_url.name, attachment_data),
        }

        response = requests.post(url, files=files2)
        # print(response.status_code)
        # print(response.content)
        if not response.status_code == 200 or response.status_code == 201:
            raise ValidationError("attachment not sent, try again")

    def send_message_attachment_url(self, recipient_id, file_type, attachment_url):
        instagram_page_access = request.env['ir.config_parameter'].sudo().get_param('pragtech_instagram_messenger.instagram_page_access')
        url = 'https://graph.facebook.com/v12.0/me/messages?access_token={}'.format(instagram_page_access)
        # print(recipient_id)

        params = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": file_type,  # audio, video, image or file
                    "payload": {
                        "url": attachment_url,
                        "is_reusable": True
                    }
                }
            }
        }

        headers = {
            'Content-type': 'application/json'
        }

        response = requests.post(url, json=params, headers=headers)
        # print(response.status_code)
        # print(response.content)
        if not response.status_code == 200 or response.status_code == 201:
            raise ValidationError("attachment not sent, try again")

    # @api.model
    # def create(self, vals):
    #     image_path = modules.get_module_resource('pragtech_instagram_messenger', 'static', 'img_45560.png')
    #     res = super(DiscussChannel, self).create(vals)
    #     # print(vals)
    #     return res

    def _execute_command_who(self, **kwargs):
        partner = self.env.user.partner_id
        members = [
            '<a href="#" data-oe-id='+str(p.id)+' data-oe-model="res.partner">@'+p.name+'</a>'
            for p in self.channel_partner_ids[:30] if p != partner
        ]
        if len(members) == 0:
            msg = _("You are alone in this channel.")
        else:
            dots = "..." if len(members) != len(self.channel_partner_ids) - 1 else ""
            msg = _("Users in this channel: %(members)s %(dots)s and you.", members=", ".join(members), dots=dots)

        self._send_transient_message(partner, msg)

    instagram_recipient_id = fields.Char(string="Recipient id")
    # time_received = fields.Datetime(string="Time received")
    channel_type = fields.Selection(
        selection_add=[("multi_livechat_NAME2", "Instagram Chat")],
        ondelete={"multi_livechat_NAME2": "cascade"}
    )
    chat_partner = fields.Many2one('res.partner', string="Partner")


class InstagramMessenger(models.Model):
    _name = 'instagram.messenger'
    _inherit = ['mail.thread']

    @api.model
    def get_chat_order(self):
        ret_list = []
        facebook_details = self.env['instagram.messenger'].sudo().search([])
        # print(facebook_details)
        for record in facebook_details:
            data_obj = {
                'name': record.username,
                'user_id': record.recipient_id,
                'id': record.id,
            }
            ret_list.append(data_obj)
        # print(ret_list)
        return ret_list
    
    # @api.model
    # def create(self, vals):
    #     res = super(InstagramMessenger, self).create(vals)
    #     self.env['mail.channel'].sudo().create({'name': vals['recipient_id'], 'channel_type': 'multi_livechat_NAME'})
    #     return res

    chat_id = fields.Many2one('chat.recipients', string='Email Alias', copy=False)
    username = fields.Char(string='Username')
    active = fields.Boolean(string='Active user', default=True)
    sender_id = fields.Char(string="Sender id")
    recipient_id = fields.Char(string="Recipient id")
    time_received = fields.Datetime(string="Time received")
    message = fields.Char(string="Message")
