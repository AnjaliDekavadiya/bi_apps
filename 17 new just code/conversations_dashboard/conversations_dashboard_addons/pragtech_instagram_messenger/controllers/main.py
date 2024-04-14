import json
import logging
import os
import time
import pytz
import datetime
from odoo.tools import ustr

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



class InstaTasks(http.Controller):
    _webhook_type = 'json'

    # def convert_epoch_to_unix_timestamp(self, msg_time):
    #     try:
    #         formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg_time))
    #         # print(formatted_time)
    #     except:
    #         formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg_time/1000))
    #         # print(formatted_time)
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
    
    @http.route('/instagram/attachments/message', type='http', auth='public', methods=['GET'], website=True)
    def attachments_route(self):
        # print(request.httprequest.args)
        if request.httprequest.method == 'GET':
            query = request.httprequest.args
            if 'attachment_id' in query:
                attachment_id = request.httprequest.args.get('attachment_id')
                attachment_data = request.env['ir.attachment'].sudo().search([('id', '=', attachment_id)])
                image_data = base64.b64decode(attachment_data.datas)
                return http.Response(image_data, status=200, content_type=attachment_data.mimetype)
            else:
                return http.Response("no attachment_id included in the request", status=430)

    def get_profile_data(self, psid, page_access_token):
        url = 'https://graph.facebook.com/{}?fields=name,profile_pic&access_token={}'.format(psid, page_access_token)
        # print(url)
        response = requests.get(url)
        # print(response.status_code)
        # print(response.content)
        return response.json()

    @http.route('/instagram/responce/message', type='http', auth='public', methods=['GET', 'POST'], website=True, csrf=False) #webhook receiving function
    def instagram_webhook(self):
        try:
            if request.httprequest.method == 'GET':
                # print("getting")
                instagram_verify_token = request.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_instagram_messenger.instagram_verify_token')
                VERIFY_TOKEN = instagram_verify_token

                if 'hub.mode' in request.httprequest.args:
                    mode = request.httprequest.args.get('hub.mode')
                    # print(mode)
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
                        challenge = request.httprequest.args.get('hub.challenge')
                        headers = {
                            'challenge': challenge
                        }
                        return http.Response(challenge, status=200)
                    else:
                        return http.Response('ERROR', status=403)

                return http.Response('SOMETHING', status=200)

            if request.httprequest.method == 'POST':
                # do something.....
                instagram_verify_token = request.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_instagram_messenger.instagram_verify_token')
                VERIFY_TOKEN = instagram_verify_token
                instagram_page_access = request.env['ir.config_parameter'].sudo().get_param(
                    'pragtech_instagram_messenger.instagram_page_access')

                if 'hub.mode' in request.httprequest.args:
                    mode = request.args.get('hub.mode')
                if 'hub.verify_token' in request.httprequest.args:
                    token = request.args.get('hub.verify_token')
                if 'hub.challenge' in request.httprequest.args:
                    challenge = request.args.get('hub.challenge')

                if 'hub.mode' in request.httprequest.args and 'hub.verify_token' in request.httprequest.args:
                    mode = request.httprequest.args.get('hub.mode')
                    token = request.httprequest.args.get('hub.verify_token')

                    if mode == 'subscribe' and token == VERIFY_TOKEN:

                        challenge = request.httprequest.args.get('hub.challenge')

                        return http.Response(challenge, status=200)
                    else:
                        return http.Response('ERROR', status=200)

                data = request.httprequest.data
                body = json.loads(data.decode('utf-8'))
                _logger.info("Data In whatsapp integration controller %s", str(body))
                if "message" in body["entry"][0]["messaging"][0]:
                    if 'is_echo' not in body["entry"][0]["messaging"][0]["message"]:
                        sender = body["entry"][0]["messaging"][0]["sender"]["id"]
                        receiver = body["entry"][0]["messaging"][0]["recipient"]["id"]
                        if 'text' in body["entry"][0]["messaging"][0]["message"]:
                            message = body["entry"][0]["messaging"][0]["message"]["text"]
                            # print(message)
                        timestamp = body["entry"][0]["time"]
                        # print(timestamp)
                        time_var = self.convert_epoch_to_unix_timestamp(int(timestamp))
                        # print(time_var)
                        profile_data = self.get_profile_data(sender, instagram_page_access)
                        _logger.info("Data In profile %s", str(profile_data))
                        if 'profile_pic' in profile_data:
                            profile_pic = profile_data['profile_pic']
                            profile_pic = profile_pic.replace("\\", "")
                            data_base64 = base64.b64encode(requests.get(profile_pic.strip()).content)
                            # print(data_base64)
                        try:
                            request.env["instagram.messenger"].sudo().create({'recipient_id': receiver, 'sender_id': sender,
                                                                             'message': message, 'time_received': time_var})
                        except:
                            request.env["instagram.messenger"].sudo().create({'recipient_id': receiver, 'sender_id': sender,
                                                                             'message': 'attachment', 'time_received': time_var})

                        partner_exists = request.env["res.partner"].sudo().search([('name', '=', profile_data['name'] if 'name' in profile_data else sender),
                                                                                   ('instagram_psid', '=', sender)])
                        if partner_exists:
                            if 'profile_pic' in profile_data:
                                partner_exists.write({'image_1920': data_base64})

                        if not partner_exists:
                            # print("creating partner")
                            if 'profile_pic' in profile_data:
                                partner = request.env["res.partner"].sudo().create({'name': profile_data['name'] if 'name' in profile_data else sender,
                                                                                    'image_1920': data_base64, 'instagram_psid': sender})
                            else:
                                partner = request.env["res.partner"].sudo().create({'name': profile_data['name'] if 'name' in profile_data else sender, 'instagram_psid': sender})
                        else:
                            partner = partner_exists

                        if 'attachments' in body["entry"][0]["messaging"][0]["message"]:
                            attachments = body["entry"][0]["messaging"][0]["message"]["attachments"]
                            # print('collecting attachments')
                            self.send_attachment_to_admin(partner, attachments)
                        elif message != '':
                            self.send_notification_to_admin(partner, message)
        except TypeError:
            return http.local_redirect('/web', query=request.params, keep_hash=True)

    def send_notification_to_admin(self, partner, msg):
        mail_channel_obj = request.env['discuss.channel']
        instagram_chat_ids = request.env.ref('pragtech_instagram_messenger.group_instagram_chat')
        instagram_chat_users_ids = instagram_chat_ids.sudo().users
        # print(instagram_chat_users_ids)
        instagram_partner_ids = instagram_chat_users_ids.mapped('partner_id')
        # print(instagram_partner_ids)
        admin_partner = request.env['res.partner'].sudo().search([('id', '=', 3)])
        # print(admin_partner)

        if partner:
            channel_exist = mail_channel_obj.sudo().search([('name', '=', 'Chat with {}'.format(partner.name)),
                                                            ('instagram_recipient_id', '=', partner.instagram_psid)], limit=1)
            if channel_exist:
                # print("posting message")
                channel_exist.with_context(from_odoobot=True).message_post(body=msg, message_type="notification",
                                                                            subtype_xmlid="mail.mt_comment",
                                                                            author_id=partner.id)
            else:
                image_path = modules.get_module_resource('pragtech_instagram_messenger', 'static', 'img_45560.png')
                image = base64.b64encode(open(image_path, 'rb').read())
                # print("creating channel")
                partner_list = []
                for instagram_partner_id in instagram_partner_ids:
                    partner_list.append(instagram_partner_id.id)
                partner_list.append(partner.id)

                if len(partner_list) > 0:
                    channel = mail_channel_obj.sudo().create({
                        'name': 'Chat with {}'.format(partner.name),
                        'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                        'channel_type': 'multi_livechat_NAME2',
                        'instagram_recipient_id': partner.instagram_psid,
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

    def send_attachment_to_admin(self, partner, attachment):
        mail_channel_obj = request.env['discuss.channel']
        instagram_chat_ids = request.env.ref('pragtech_instagram_messenger.group_instagram_chat')
        instagram_chat_users_ids = instagram_chat_ids.sudo().users
        # print(instagram_chat_users_ids)
        instagram_partner_ids = instagram_chat_users_ids.mapped('partner_id')
        # print(instagram_partner_ids)
        admin_partner = request.env['res.partner'].sudo().search([('id', '=', 3)])
        # print(admin_partner)

        if partner:
            channel_exist = mail_channel_obj.sudo().search([('name', '=', 'Chat with {}'.format(partner.name)),
                                                            ('instagram_recipient_id', '=', partner.instagram_psid)], limit=1)
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
                     'create_uid': instagram_chat_users_ids.id, 'public': True})
                # print(attachment.create_uid)
                # print(attachment.id)
                channel_exist.with_context(from_odoobot=True).message_post(body=attachment.url, attachment_ids=[attachment.id], message_type="notification",
                                                                           subtype_xmlid="mail.mt_comment", author_id=partner.id)
            else:
                image_path = modules.get_module_resource('pragtech_instagram_messenger', 'static', 'img_45560.png')
                image = base64.b64encode(open(image_path, 'rb').read())
                # print("creating channel")
                partner_list = []
                for instagram_chat_partner_id in instagram_partner_ids:
                    partner_list.append(instagram_chat_partner_id.id)
                partner_list.append(partner.id)
                # print(partner_list)

                if len(partner_list) > 0:
                    channel = mail_channel_obj.sudo().create({
                        'name': 'Chat with {}'.format(partner.name),
                        'channel_partner_ids': [(6, 0, partner_id) for partner_id in partner_list],
                        'channel_type': 'multi_livechat_NAME2',
                        'instagram_recipient_id': partner.instagram_psid,
                        'chat_partner': partner.id,
                        # 'public': 'public',
                        'image_128': image,
                    })
                    attachment = request.env['ir.attachment'].sudo().create(
                        {'name': 'facebook attachment', 'res_id': channel.id, 'res_model': 'discuss.channel',
                        'type': 'url', 'url': attachment[0]['payload']['url'], 'create_uid': instagram_chat_users_ids.id})
                    # print(attachment.mimetype)
                    channel.with_context(from_odoobot=True).message_post(body=attachment.url, attachment_ids=[attachment.id],
                                                                          message_type="notification",
                                                                          subtype_xmlid="mail.mt_comment",
                                                                          author_id=partner.id)
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
