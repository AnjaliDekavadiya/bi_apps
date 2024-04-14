import json
import base64
import requests
import logging
import io
import os
import mimetypes
from werkzeug.exceptions import NotFound, Forbidden
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)

from odoo.addons.pragtech_whatsapp_base.controller.main import WhatsappBase

class AttachmentGlobalUrl(http.Controller):

    # @http.route([
    #     '/web/whatsapp_logo',
    # ], type='http', auth="none", cors="*")
    # def company_logo(self, dbname=None, **kw):
    #     response = http.Stream.from_path(file_path('pragmatic_odoo_whatsapp_integration/static/img/whatsapp_background.png')).get_response()
    #     return response

    @http.route(['/whatsapp_attachment/<string:whatsapp_access_token>/get_attachment'], type='http', auth='public')
    def social_post_instagram_image(self, whatsapp_access_token):
        social_post = request.env['ir.attachment'].sudo().search(
            [('access_token', '=', whatsapp_access_token)])

        if not social_post:
            raise Forbidden()

        if social_post["type"] == "url":
            if social_post["url"]:
                return request.redirect(social_post["url"])
            else:
                return request.not_found()
        elif social_post["datas"]:
            data = io.BytesIO(base64.standard_b64decode(social_post["datas"]))
            # we follow what is done in ir_http's binary_content for the extension management
            extension = os.path.splitext(social_post["name"] or '')[1]
            extension = extension if extension else mimetypes.guess_extension(social_post["mimetype"] or '')
            filename = social_post['name']
            filename = filename if os.path.splitext(filename)[1] else filename + extension
            return http.send_file(data, filename=filename, as_attachment=True)
        else:
            return request.not_found()

class WhatsappMarketing(WhatsappBase):

    @http.route(['/whatsapp/response/message'], type='json', auth='public')
    def whatsapp_responce(self):
        super(WhatsappMarketing, self).whatsapp_response()
        data = json.loads(request.httprequest.data)
        request.env['whatsapp.msg.res.partner']._default_unique_user()
        _request = data
        if 'messages' in data and data['messages']:
            msg_list = []
            msg_dict = {}
            whatsapp_contact_obj = request.env['whatsapp.contact']
            odoo_group_obj = request.env['odoo.group']
            whatapp_msg = request.env['whatsapp.messages']
            for msg in data['messages']:
                # if msg.get('fromMe'):
                #     continue
                if 'chatId' in msg and msg['chatId'] and not msg.get('fromMe'):
                    whatsapp_contact_obj = whatsapp_contact_obj.sudo().search([('whatsapp_id', '=', msg['chatId'])], limit=1)
                    msg_dict = {
                        'name': msg['body'],
                        'message_id': msg['id'],
                        'fromMe': msg['fromMe'],
                        'to': msg['chatName'] if msg['fromMe'] == True else 'To Me',
                        'chatId': msg['chatId'],
                        'type': msg['type'],
                        'senderName': msg['senderName'],
                        'chatName': msg['chatName'],
                        'author': msg['author'],
                        'time': self.convert_epoch_to_unix_timestamp(int(msg['time'])),
                        'state': 'sent' if msg['fromMe'] == True else 'received',
                    }
                    if whatsapp_contact_obj:
                        if msg['type'] == 'image' and whatsapp_contact_obj:
                            url = msg['body']
                            image_data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                            msg_dict.update({'message_body': msg['caption'], 'whatsapp_contact_id': whatsapp_contact_obj.id, 'msg_image': image_data })
                        if whatsapp_contact_obj and msg['type'] == 'chat':
                            msg_dict.update({ 'message_body': msg['body'], 'whatsapp_contact_id': whatsapp_contact_obj.id })


                    if len(msg_dict) > 0:
                        msg_list.append(msg_dict)
            for msg in msg_list:
                whatapp_msg_id = whatapp_msg.sudo().search([('message_id', '=', msg.get('message_id'))])
                if whatapp_msg_id:
                    whatapp_msg_id.sudo().write(msg)
                    _logger.info("whatapp_msg_id write %s: ", str(whatapp_msg_id))
                    if data.get('messages'):
                        for msg in data['messages']:
                            if whatapp_msg_id and msg['type'] == 'document':
                                msg_attchment_dict = {}
                                url = msg['body']
                                data_base64 = base64.b64encode(requests.get(url.strip()).content)
                                msg_attchment_dict = {'name': msg['caption'], 'datas': data_base64, 'type': 'binary',
                                                      'res_model': 'whatsapp.messages', 'res_id': whatapp_msg_id.id}
                                attachment_id = request.env['ir.attachment'].sudo().create(msg_attchment_dict)
                                res_update_whatsapp_msg = whatapp_msg_id.sudo().write({'attachment_id': attachment_id.id})
                                _logger.info("res_update_whatsapp_msg %s: ", str(res_update_whatsapp_msg))
                else:
                    res_create = whatapp_msg.sudo().create(msg)
                    _logger.info("In whatsapp_marketing_message res_create %s: ", str(res_create))
        return 'OK'
