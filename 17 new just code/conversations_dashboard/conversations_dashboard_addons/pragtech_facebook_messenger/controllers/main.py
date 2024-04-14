import json
import logging
import os
import time
import pytz
import datetime
from odoo.tools import ustr
from odoo.tools import misc

import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest

from odoo import api, http, SUPERUSER_ID, _, modules
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo import registry as registry_get
import requests
import base64

from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home

_logger = logging.getLogger(__name__)

os.environ['FACEBOOK_PAGE_ID'] = "768992743144691"

os.environ['FACEBOOK_APP_ID'] = "410854733883981"
os.environ['FACEBOOK_PAGE_ACCESS_TOKEN'] = "EAAF1q5J3qk0BABh0DSPaNEvZAFJ4SfWzBbQCncfjhPJYBwsdqfgO4mKuuUkEZCc4PSZCPoiAQyUsZB9mzWzKtsoVJGrva1XZCblaCkzAnt7aX9kBR7As08Bsm4Eq3FN78ukc0LDySvG3nTAJgKBZCdHkBh63hKDltrrpxXVGr6pZCBRNTM7edthbAshTyLyoN2WUYrQ5yhQTAZDZD"
os.environ['FACEBOOK_APP_SECRET'] = "2bbf3f9bc50573287a00f28ac769ea45"



class MessengerTasks(http.Controller):
    _webhook_type = 'json'

    @http.route('/testing/posting/message', type='json', auth='public', methods=['GET', 'POST'],
                website=True)  # webhook receiving function
    def testing_post_webhook(self):
        if request.httprequest.method == 'POST':
            test_json = {'names': 'Test name', 'email': 'Test email', 'phone': 'Test phone', 'ID': 'test ID'}
            test_json = json.dumps(test_json)
            return http.Response(test_json, status=200)

    @http.route('/testing/responce/message', type='http', auth='public', methods=['GET', 'POST'],
                website=True)  # webhook receiving function
    def testing_webhook(self):
        if request.httprequest.method == 'GET':
            test_json = {'names': 'Test name', 'email': 'Test email', 'phone': 'Test phone', 'ID': "12"}
            test_json = json.dumps(test_json)

            return http.Response(test_json, status=200)
        if request.httprequest.method == 'POST':
            test_json = {'names': 'Test name', 'email': 'Test email', 'phone': 'Test phone', 'ID': 'test ID'}
            test_json = json.dumps(test_json)
            return http.Response(test_json, status=200)

    # def convert_epoch_to_unix_timestamp(self, msg_time):
    #     try:
    #         formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg_time))
    #     except:
    #         formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg_time/1000))
    #     date_time_obj = datetime.datetime.strptime(formatted_time, '%Y-%m-%d %H:%M:%S')
    #     dt = False
    #     if date_time_obj:
    #         timezone = pytz.timezone(request.env['res.users'].sudo().browse([int(2)]).tz or 'UTC')
    #     dt = pytz.UTC.localize(date_time_obj)
    #     dt = dt.astimezone(timezone)
    #     dt = ustr(dt).split('+')[0]
    #     return date_time_obj

    def convert_epoch_to_unix_timestamp(self, msg_time):
        try:
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(msg_time) / 1000))
        except:
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(msg_time)))
        date_time_obj = datetime.datetime.strptime(formatted_time, '%Y-%m-%d %H:%M:%S')
        dt = False
        if date_time_obj:
            timezone = pytz.timezone(request.env['res.users'].sudo().browse([int(2)]).tz or 'UTC')
        dt = pytz.UTC.localize(date_time_obj)
        dt = dt.astimezone(timezone)
        dt = ustr(dt).split('+')[0]
        return date_time_obj

    def get_webhook_type(self):
        webhook_verified = request.env['ir.config_parameter'].sudo().get_param(
            'pragtech_facebook_messenger.webhook_verified')
        if webhook_verified:
            webhook_type = 'json'
        else:
            webhook_type = 'http'
        return webhook_type

    def get_profile_data(self, psid, page_access_token):
        url = 'https://graph.facebook.com/{}?fields=first_name,last_name,profile_pic&access_token={}'.format(psid, page_access_token)
        response = requests.get(url)
        return response.json()

    @http.route('/facebook/responce/message', type='http', auth='public', methods=['GET', 'POST'], website=True,csrf=False) #webhook receiving function
    def facebook_webhook(self):
        try:
            if request.httprequest.method == 'GET':
                # print("getting")
                facebook_verify_token = request.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_facebook_messenger.facebook_verify_token')
                VERIFY_TOKEN = facebook_verify_token

                if 'hub.mode' in request.httprequest.args:
                    mode = request.httprequest.args.get('hub.mode')
                if 'hub.verify_token' in request.httprequest.args:
                    token = request.httprequest.args.get('hub.verify_token')
                    # print(token)
                if 'hub.challenge' in request.httprequest.args:
                    challenge = request.httprequest.args.get('hub.challenge')
                    # print(challenge)

                if 'hub.mode' in request.httprequest.args and 'hub.verify_token' in request.httprequest.args:
                    mode = request.httprequest.args.get('hub.mode')
                    token = request.httprequest.args.get('hub.verify_token')

                    if mode == 'subscribe' and token == VERIFY_TOKEN:
                        # print('WEBHOOK VERIFIED')

                        challenge = request.httprequest.args.get('hub.challenge')
                        # print(challenge)
                        # print(http.Response(challenge, status=200))
                        # headers = {
                        #     'challenge': challenge
                        # }
                        return http.Response(challenge, status=200)

                        #return challenge, 200
                    else:
                        return http.Response('ERROR', status=403)

                test_json = {'names': 'Test name', 'email': 'Test email', 'phone': 'Test phone', 'ID': 'test ID'}
                test_json = json.loads(test_json)
                # print(test_json)

                return http.Response(test_json, status=200)#'SOMETHING', 200

            if request.httprequest.method == 'POST':
                # do something.....
                # print("posting")

                facebook_verify_token = request.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_facebook_messenger.facebook_verify_token')
                VERIFY_TOKEN = facebook_verify_token
                facebook_page_access = request.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_facebook_messenger.facebook_page_access')

                # print(VERIFY_TOKEN)
                # print(facebook_page_access)

                if 'hub.mode' in request.httprequest.args:
                    mode = request.args.get('hub.mode')
                    # print(mode)
                if 'hub.verify_token' in request.httprequest.args:
                    token = request.args.get('hub.verify_token')
                    # print(token)
                if 'hub.challenge' in request.httprequest.args:
                    challenge = request.args.get('hub.challenge')
                    # print(challenge)

                if 'hub.mode' in request.httprequest.args and 'hub.verify_token' in request.httprequest.args:
                    mode = request.httprequest.args.get('hub.mode')
                    token = request.httprequest.args.get('hub.verify_token')

                    if mode == 'subscribe' and token == VERIFY_TOKEN:
                        # print('WEBHOOK VERIFIED')

                        challenge = request.httprequest.args.get('hub.challenge')

                        return http.Response(challenge, status=200)
                    else:
                        return 'ERROR', 403

                # do something else
                data = request.httprequest.data
                body = json.loads(data.decode('utf-8'))
                _logger.info("Data In facebook integration controller %s", str(body))
                if body["entry"][0]["messaging"][0].get('message') and not body["entry"][0]["messaging"][0].get('message').get('app_id'):
                    sender = body["entry"][0]["messaging"][0]["sender"]["id"]
                    receiver = body["entry"][0]["messaging"][0]["recipient"]["id"]
                    if 'text' in body["entry"][0]["messaging"][0]["message"]:
                        message = body["entry"][0]["messaging"][0]["message"]["text"]
                        # print(message)
                    timestamp = body["entry"][0]["time"]
                    # print(timestamp)
                    time_var = self.convert_epoch_to_unix_timestamp(int(timestamp))
                    # print(time_var)
                    profile_data = self.get_profile_data(sender, facebook_page_access)
                    if 'profile_pic' in profile_data:
                        profile_pic = profile_data['profile_pic']
                        profile_pic = profile_pic.replace("\\", "")
                        data_base64 = base64.b64encode(requests.get(profile_pic.strip()).content)
                        # print(data_base64)
                    # print(profile_data)
                    try:
                        facebook_msg_id = request.env["facebook.messenger"].sudo().create({'recipient_id': receiver, 'sender_id': sender,
                                                                         'message': message, 'time_received': time_var})
                    except:
                        facebook_msg_id = request.env["facebook.messenger"].sudo().create({'recipient_id': receiver, 'sender_id': sender,
                                                                         'message': 'attachment', 'time_received': time_var})

                    partner_exists = request.env["res.partner"].sudo().search([('name', '=', profile_data.get('first_name')),
                                                                               ('facebook_psid', '=', sender)])

                    if partner_exists:
                        if 'profile_pic' in profile_data:
                            partner_exists.write({'image_1920': data_base64})

                    if not partner_exists:
                        if 'profile_pic' in profile_data:
                            partner = request.env["res.partner"].sudo().create(
                                {'name': profile_data['first_name'], 'facebook_psid': sender, 'image_1920': data_base64})
                        else:
                            partner = request.env["res.partner"].sudo().create({'name': profile_data.get('first_name'), 'facebook_psid': sender})
                    else:
                        partner = partner_exists

                    if 'attachments' in body["entry"][0]["messaging"][0]["message"]:
                        attachments = body["entry"][0]["messaging"][0]["message"]["attachments"]
                        # print('collecting attachments')
                        self.send_attachment_to_admin(partner, attachments, facebook_msg_id)
                    elif message != '':
                        self.send_notification_to_admin(partner, message)
        except TypeError:
            return http.local_redirect('/web', query=request.params, keep_hash=True)

    def send_notification_to_admin(self, partner, msg):
        mail_channel_obj = request.env['discuss.channel']
        facebook_chat_ids = request.env.ref('pragtech_facebook_messenger.group_facebook_chat')
        facebook_chat_users_ids = facebook_chat_ids.sudo().users
        # print(facebook_chat_users_ids)
        facebook_partner_ids = facebook_chat_users_ids.mapped('partner_id')
        # print(facebook_partner_ids)
        admin_partner = request.env['res.partner'].sudo().search([('name', '=', "Administrator")], order="id", limit=1)
        # print(admin_partner)
        if partner:
            channel_exist = mail_channel_obj.sudo().search([('name', '=', 'Chat with {}'.format(partner.name)),
                                                            ('facebook_recipient_id', '=', partner.facebook_psid)], limit=1)
            # print(channel_exist)
            if channel_exist:
                # print("posting message")
                channel_exist.with_context(from_odoobot=True).message_post(body=msg, message_type="notification",
                                                                            subtype_xmlid="mail.mt_comment",
                                                                            author_id=partner.id)
            else:
                # image_path = modules.get_module_resource('pragtech_facebook_messenger', 'static', 'social_media_logo_facebook_icon-icons.com_59059.png')
                image_path = misc.file_path('pragtech_facebook_messenger/static/social_media_logo_facebook_icon-icons.com_59059.png')
                image = base64.b64encode(open(image_path, 'rb').read())
                # print("creating channel")
                partner_list = []
                for facebook_chat_partner_id in facebook_partner_ids:
                    partner_list.append(facebook_chat_partner_id.id)
                partner_list.append(partner.id)
                # print(partner_list)

                if len(partner_list) > 0:
                    channel = mail_channel_obj.sudo().create({
                        'name': 'Chat with {}'.format(partner.name),
                        'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                        'channel_type': 'multi_livechat_NAME',
                        'facebook_recipient_id': partner.facebook_psid,
                        'chat_partner': partner.id,
                        # 'public': 'public',
                        'image_128': image,
                    })
                    channel.with_context(from_odoobot=True).message_post(body=msg,
                                                                          message_type="notification",
                                                                          subtype_xmlid="mail.mt_comment",
                                                                          author_id=partner.id)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }

    def send_attachment_to_admin(self, partner, attachment, facebook_msg_id):
        mail_channel_obj = request.env['discuss.channel']
        facebook_chat_ids = request.env.ref('pragtech_facebook_messenger.group_facebook_chat')
        facebook_chat_users_ids = facebook_chat_ids.sudo().users
        # print(facebook_chat_users_ids)
        facebook_partner_ids = facebook_chat_users_ids.mapped('partner_id')
        # print(facebook_partner_ids)
        admin_partner = request.env['res.partner'].sudo().search([('id', '=', 3)])
        # print(admin_partner)

        if partner:
            channel_exist = mail_channel_obj.sudo().search([('name', '=', 'Chat with {}'.format(partner.name)),
                                                            ('facebook_recipient_id', '=', partner.facebook_psid)], limit=1)
            # print(channel_exist)
            if channel_exist:
                # print("posting attachment")
                try:
                    url = attachment[0]['payload']['url']
                    image = base64.b64encode(requests.get(url.strip()).content)
                    # print(image)
                except:
                    image = requests.get(attachment[0]['payload']['url'])
                    image = image.content
                    image = base64.b64encode(image)
                    # print(image)

                attachment = request.env['ir.attachment'].sudo().create(
                    {'name': 'facebook attachment', 'res_id': channel_exist.id, 'res_model': 'discuss.channel',
                    'type': 'binary', 'datas': image, 'url': attachment[0]['payload']['url'],
                     'create_uid': facebook_chat_users_ids.id, 'public': True})
                # print(attachment.create_uid)
                # attachment_id = request.env['ir.attachment'].sudo().create(msg_attchment_dict)
                facebook_msg_id.sudo().write({'attachment_id': attachment.id})
                channel_exist.with_context(from_odoobot=True).message_post(body=attachment.url, attachment_ids=[attachment.id], message_type="notification",
                                                                           subtype_xmlid="mail.mt_comment", author_id=partner.id)
            else:
                # image_path = modules.get_module_resource('pragtech_facebook_messenger', 'static', 'social_media_logo_facebook_icon-icons.com_59059.png')
                image_path = misc.file_path('pragtech_facebook_messenger/static/social_media_logo_facebook_icon-icons.com_59059.png')
                image = base64.b64encode(open(image_path, 'rb').read())
                # print("creating channel")
                partner_list = []
                for facebook_chat_partner_id in facebook_partner_ids:
                    partner_list.append(facebook_chat_partner_id.id)
                partner_list.append(partner.id)

                if len(partner_list) > 0:
                    channel = mail_channel_obj.sudo().create({
                        'name': 'Chat with {}'.format(partner.name),
                        'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                        'channel_type': 'multi_livechat_NAME',
                        'facebook_recipient_id': partner.facebook_psid,
                        'chat_partner': partner.id,
                        # 'public': 'public',
                        'image_128': image,
                    })
                    attachment = request.env['ir.attachment'].sudo().create(
                        {'name': 'facebook attachment', 'res_id': channel.id, 'res_model': 'discuss.channel',
                         'type': 'url', 'url': attachment[0]['payload']['url'], 'create_uid': facebook_chat_users_ids.id})
                    facebook_msg_id.sudo().write({'attachment_id': attachment.id})
                    channel.with_context(from_odoobot=True).message_post(body=attachment.url, attachment_ids=[attachment.id],
                                                                          message_type="notification",
                                                                          subtype_xmlid="mail.mt_comment",
                                                                          author_id=partner.id)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
