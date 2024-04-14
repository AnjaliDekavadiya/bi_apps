from odoo import api, fields, models, SUPERUSER_ID, modules, _, http
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
import requests
import re
import json


class ResPartner(models.Model):
    _inherit = 'res.partner'

    facebook_psid = fields.Char(string="Messenger PSID")


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    # def facebook_channel_create(self, name, channel_type, privacy='public'):
    #     new_channel = self.create({
    #         'name': name,
    #         'public': privacy,
    #         'email_send': False,
    #         'channel_type': channel_type
    #     })
    #     notification = _(
    #         '<div class="o_mail_notification">created <a href="#" class="o_channel_redirect" data-oe-id="%s">#%s</a></div>',
    #         new_channel.id, new_channel.name)
    #     new_channel.message_post(body=notification, message_type="notification", subtype_xmlid="mail.mt_comment")
    #     channel_info = new_channel.channel_info('creation')[0]
    #     self.env['bus.bus'].sendone((self._cr.dbname, 'res.partner', self.env.user.partner_id.id), channel_info)
    #     return channel_info

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
        # print(base_url)
        if not self._context.get('from_odoobot'):
            if kwargs.get('attachment_ids'):
                message.write({"message_type": "comment"})
            if self.channel_type == 'multi_livechat_NAME':
                # print("sending to facebook.....")
                if self.facebook_recipient_id:
                    if message.attachment_ids:
                        # print("sending attachment")
                        #print(message.attachment_ids.datas)
                        if 'png' in message.attachment_ids.mimetype or 'jpg' in message.attachment_ids.mimetype or 'jpeg' in message.attachment_ids.mimetype:
                            file_type = 'image'
                        elif 'mp4' in message.attachment_ids.mimetype or '3gp' in message.attachment_ids.mimetype or 'avi' in message.attachment_ids.mimetype:
                            file_type = 'video'
                        else:
                            file_type = 'file'
                        self.send_message_attachment_file2(self.facebook_recipient_id, file_type, message.attachment_ids)   # base_url+message.attachment_ids.local_url
                    if message.body:
                        # print("sending to ", self.facebook_recipient_id)
                        self.send_facebook_text_message(self.facebook_recipient_id, kwargs, message)
                        # self.env['facebook.messenger'].send_text_message(self.name, message.body)
                else:
                    ValidationError(" No facebook id defined for this recipient")
        return message

    def convert_email_from_to_name(self, str1):
        result = re.search('"(.*)"', str1)
        return result.group(1)

    def custom_html2plaintext(self, html):
        html = re.sub('<br\s*/?>', '\n', html)
        html = re.sub('<.*?>', ' ', html)
        return html

    def send_facebook_text_message(self, recipient_id, kwargs, message):
        # url format is 'https://graph.facebook.com/v13.0/me/messages?access_token=<PAGE_ACCESS_TOKEN>'
        html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))
        # print(html_to_plain_text)
        # print(recipient_id)
        facebook_page_access = self.env['ir.config_parameter'].sudo().get_param('pragtech_facebook_messenger.facebook_page_access')
        # print(facebook_page_access)
        if facebook_page_access:
            page_access_token = 'EAAEUmrRw3NsBADPZAGmtWNF8ri5POyFGZBNDjHqMpqGOJRlnSUgBFlzMRrns9pVrw2Vb5lR7Bh08LMO9PSO7YI2sv6dvrZBllAKybyPDwFIBHPKZC4PmbolA5g2xs19ZCM9gh3hPntsfvx0pbAobhuQ37QPNZBlShdWus4dWHpH2NAjYgzyAvY'
            url = 'https://graph.facebook.com/v12.0/me/messages?access_token={}'.format(facebook_page_access)
            # recipient_id = self.env['facebook.messenger'].search([('username', '=', recipient_name)])
            # recipient_id = self.recipient_id
            params = {
                "messaging_type": "RESPONSE",
                "recipient": {
                    "id": recipient_id  # <PSID>
                },
                "message": {
                    "text": html_to_plain_text
                }
            }

            headers = {'content-type': 'application/json'}
            response = requests.post(url, json=params, headers=headers)
            # print(response.status_code)
            # print(response.content)
            if response.status_code == 200 or response.status_code == 201:
                self.env["facebook.messenger"].sudo().create({
                    'recipient_id': recipient_id,
                    'sender_id': self.env.user.id,
                    'message': message,
                    'time_received': fields.Datetime.now()
                    })
            else:
                raise ValidationError("message not sent, try again")

    def send_facebook_message_attachment_url(self, recipient_id, file_type, attachment_url):
        facebook_page_access = self.env['ir.config_parameter'].sudo().get_param('pragtech_facebook_messenger.facebook_page_access')
        url = 'https://graph.facebook.com/v12.0/me/message_attachments?access_token={}'.format(facebook_page_access)
        # print(recipient_id)
        # print(file_type)
        # print(attachment_url)
        tempfilename = "/tmp/test.png"

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

    def send_message_attachment_file2(self, recipient_id, file_type, attachment_url):
        facebook_page_access = self.env['ir.config_parameter'].sudo().get_param('pragtech_facebook_messenger.facebook_page_access')
        url = 'https://graph.facebook.com/v12.0/me/messages?access_token={}'.format(facebook_page_access)
        # print(file_type)
        attachment_data = base64.b64decode(attachment_url.datas)
        recipient = {
                "id": recipient_id
            }
        message = {
                "attachment": {
                    "type": 'file',  # audio, video, image or file
                    "payload": {
                        "is_reusable": True
                    }
                }
            }

        files2 = {
            'recipient': (None, json.dumps(recipient)),
            'message': (None, json.dumps(message), 'application/json'),
            'filedata': (attachment_url.name, attachment_data),
        }

        headers = {
            'Content-type': 'multipart/form-data'
        }

        response = requests.post(url, files=files2)
        # print(response.status_code)
        if response.status_code == 200 or response.status_code == 201:
            self.env["facebook.messenger"].sudo().create({
                    'recipient_id': recipient_id,
                    'attachment_data' : attachment_data,
                    'sender_id': self.env.user.id,
                    'message': attachment_url.name,
                    'time_received': fields.Datetime.now()
                })
        else:
            raise ValidationError("attachment not sent, try again")

    @api.model
    def create(self, vals):
        image_path = modules.get_module_resource('pragtech_facebook_messenger', 'static', 'social_media_logo_facebook_icon-icons.com_59059.png')
        res = super(DiscussChannel, self).create(vals)
        return res

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

    facebook_recipient_id = fields.Char(string="Recipient id")
    time_received = fields.Datetime(string="Time received")
    message = fields.Char(string="Message")
    channel_type = fields.Selection(
        selection_add=[("multi_livechat_NAME", "Facebook Chat")],
        ondelete={"multi_livechat_NAME": "cascade"}, readonly=False
    )


class FacebookMessenger(models.Model):
    _name = 'facebook.messenger'
    # _inherit = ['mail.thread']

    @api.model
    def get_chat_order(self):
        ret_list = []
        facebook_details = self.env['facebook.messenger'].sudo().search([])
        # print(facebook_details)
        # req = (
        #     "SELECT facebook_messenger.name, rp.name AS customer, sale_order.amount_total, sale_order.state "
        #     "FROM facebook_messenger "
        #     "Join res_partner rp ON (sale_order.partner_id=rp.id)")
        # self.env.cr.execute(req)
        # for rec in self.env.cr.dictfetchall():
        #     ret_list.append(rec)
        # return ret_list
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
    #     res = super(FacebookMessenger, self).create(vals)
    #     self.env['mail.channel'].sudo().create({'name': vals['recipient_id'], 'channel_type': 'multi_livechat_NAME'})
    #     # http.local_redirect('/web', query=request.params, keep_hash=True)
    #     return res

    def add_new_chat(self):
        """makes api call"""
        user_id = "Sample id from api call"
        username = "Sample username from api call"
        self.env['chat.recipients'].sudo().create({'recipient_id': self.recipient_id, 'recipient_username': username})

    # alias_user_id = fields.Many2one('res.users')
    # chat_id = fields.Many2one('chat.recipients', string='Email Alias', copy=False)
    # username = fields.Char(string='Username')
    active = fields.Boolean(string='Active user', default=True)
    sender_id = fields.Char(string="Sender id")
    recipient_id = fields.Char(string="Recipient id")
    time_received = fields.Datetime(string="Time received")
    message = fields.Char(string="Message")
    attachment_id = fields.Many2one('ir.attachment', 'Attachment ', readonly=True)
    attachment_data = fields.Binary(related='attachment_id.datas', string='Attachment', readonly=True)


class ChatRecipients(models.Model):
    _name = 'chat.recipients'
    _inherit = ['mail.thread', 'mail.alias.mixin']
    _description = 'Chat Recipients'

    name = fields.Char(tracking=True)
    partner_id = fields.Many2one('res.partner', 'Responsible',
                                 tracking=True)
    guest_ids = fields.Many2many('res.partner', 'Participants')
    state = fields.Selection([('draft', 'New'), ('confirmed', 'Confirmed')],
                             tracking=True)
    # expense_ids = fields.One2many('facebook.messenger', 'chat_id', 'Expenses')
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict",
                               required=True)

    def _get_alias_model_name(self, vals):
        """ Specify the model that will get created when the alias receives a message """
        return 'facebook.messenger'

    def _get_alias_values(self):
        """ Specify some default values that will be set in the alias at its creation """
        values = super(ChatRecipients, self).sudo()._get_alias_values()
        # alias_defaults holds a dictionary that will be written
        # to all records created by this alias
        #
        # in this case, we want all expense records sent to a trip alias
        # to be linked to the corresponding business trip
        values['alias_defaults'] = {'trip_id': self.id}
        values['alias_contact'] = 'followers'
        return values
