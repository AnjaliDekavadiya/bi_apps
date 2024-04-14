from odoo import api, fields, models, _
import requests
import json
import logging
import base64
import re
from odoo import tools
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError
from requests.structures import CaseInsensitiveDict
from odoo.osv import expression

class mailChannel(models.Model):
    _inherit = 'discuss.channel'

    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, message_type='comment', **kwargs):
        message = super(mailChannel, self).message_post(message_type='comment', **kwargs)
        self_name = self.name
        number = self_name.replace('Chat with ','')
        mobile = self.env['res.partner'].search([('name', '=', number)]).mobile
        # print(self.name)
        # print(kwargs.get('author_id'))
        if not self._context.get('from_odoobot'):
            if kwargs.get('attachment_ids'):
                message.write({"message_type": "comment"})
            if self.channel_type == 'multi_livechat_NAMEs':
                config_settings = self.env['res.config.settings'].sudo().get_values()
                api_selection = config_settings.get('api_selection')
                if api_selection == '1msg':
                    self.send_whatsapp_message(mobile, kwargs, message)
                elif api_selection == 'meta':
                    if kwargs.get('attachment_ids'):
                        message.write({"message_type": "comment"})
                        self.send_whatsapp_meta_message_attachment_url(mobile, message.attachment_ids, message.body)
                    else:
                        self.send_whatsapp_meta_text_message(mobile, kwargs, message)
                # self.send_whatsapp_message(self.chat_partner, kwargs, message)
        # if self.channel_type == 'multi_livechat_NAME':
        #     self.send_whatsapp_message(self.channel_partner_ids, kwargs, message)
        return message

    def convert_email_from_to_name(self, str1):
        result = re.search('"(.*)"', str1)
        return result.group(1)

    def custom_html2plaintext(self, html):
        html = re.sub('<br\s*/?>', '\n', html)
        html = re.sub('<.*?>', ' ', html)
        return html

    def send_whatsapp_meta_text_message(self, number, kwargs, attachment_ids):
        html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))
        whatsapp_page_access = self.env['ir.config_parameter'].sudo().get_param('pragtech_whatsapp_messenger.whatsapp_page_access')
        config_settings = self.env['res.config.settings'].sudo().get_values()
        token = config_settings.get('whatsapp_meta_api_token')
        if token:
            config_settings = self.env['res.config.settings'].sudo().get_values()
            number_id = config_settings.get('whatsapp_meta_phone_number_id')
            url = "https://graph.facebook.com/v17.0/{}/messages".format(number_id)
            req_headers = CaseInsensitiveDict()
            req_headers["Authorization"] = "Bearer " + token
            req_headers["Content-Type"] = "application/json"

            # data_json = {
            #     "messaging_product": "whatsapp",
            #     "recipient_type": "individual",
            #     "to": number,
            #     "type": "text",
            #     "text": {
            #         "body": html_to_plain_text,
            #     }
            # }
            data_json = {
                    "messaging_product": "whatsapp",
                    "to": number,
                    "type": "template",
                    "template": {
                        "name": html_to_plain_text,
                        "language": {
                            "code": "en_US"
                        }
                    }
                }
                
            data_json_open = {
                "messaging_product": "whatsapp",
                "to": number,
                "text": {"body": html_to_plain_text},
            }
            response = requests.post(url, headers=req_headers, json=data_json)
            if response.status_code in [202, 201, 200]:
                _logger.info("\nSend Message successfully")
            else:
                result = requests.post(url, headers=req_headers, json=data_json_open)
                _logger.info("\nJson Response: {}".format(result.json()))
                log_message = "Json Response:{}".format(result.json())
                # terminal_log_obj.log_info(log_message)
                if result.status_code == 200 or result.status_code == 201:
                    _logger.info("\nSend message successful")
                else:
                    raise ValidationError(str(result.status_code)+" Error occured, pls try again")

    def send_whatsapp_meta_message_attachment_url(self, number, file_data, message):
        whatsapp_page_access = self.env['ir.config_parameter'].sudo().get_param('pragtech_whatsapp_messenger.whatsapp_page_access')
        url = 'https://graph.facebook.com/v12.0/me/message_attachments?access_token={}'.format(whatsapp_page_access)
        tempfilename = "/tmp/test.png"
        for attachment in file_data:

            config_settings = self.env['res.config.settings'].sudo().get_values()
            number_id = config_settings.get('whatsapp_meta_phone_number_id')
            token = config_settings.get('whatsapp_meta_api_token')
            url = "https://graph.facebook.com/v17.0/{}/messages".format(number_id)
            attachment_data = base64.b64decode(attachment.datas)
            req_headers = CaseInsensitiveDict()
            req_headers[
                "Authorization"] = "Bearer " + token
            req_headers["Content-Type"] = "application/json"
            files2 = {
                # 'messaging_product': "whatsapp",
                'file': (attachment.name, attachment_data, attachment.mimetype, {'Expires': '0'}),
            }
            param = {
                'messaging_product': "whatsapp"
            }
            # headers = {
            #     "Authorization": "Bearer {}".format(whatsapp_page_access)
            # }
            # result = requests.post(url, headers=req_headers, files=files2, data=param)
            # result_json = result.json()
            # obj_id = result_json["id"]
            if file_data:
                for attachment in file_data:
                    data_json = {
                                    "messaging_product": "whatsapp",
                                    "recipient_type": "individual",
                                    "to": number,
                                    "type": "image",
                                    "image": {
                                        "link": attachment.public_url,
                                        "caption": attachment.name
                                        # "filename": file_name
                                    }
                                }
                if attachment.mimetype in ['application/pdf', 'application/zip',
                                               'application/vnd.oasis.opendocument.text',
                                               'application/msword']:
                    data_json = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": number,
                        "type": "document",
                        "document": {
                            "link": attachment.public_url,
                            "caption": attachment.name
                        }
                    }
            # new_url = "https://graph.facebook.com/v15.0/{}/messages".format(number_id)
            response = requests.post(url, headers=req_headers, json=data_json)
            if response.status_code in [202, 201, 200]:
                _logger.info("\nSend Message successfully")

    def send_whatsapp_message(self, partner_ids, kwargs, message_id):
        # print('---sending whatsapp message')
        if 'author_id' in kwargs and kwargs.get('author_id'):
            partner_id = self.env['res.partner'].search([('id', '=', kwargs.get('author_id'))])
            param = self.env['res.config.settings'].sudo().get_values()
            no_phone_partners = []
            invalid_whatsapp_number_partner = []
            if param.get('whatsapp_endpoint') and param.get('whatsapp_token'):
                status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
                status_response = requests.get(status_url)
                json_response_status = json.loads(status_response.text)
                # print("author found", json_response_status)
                if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status['accountStatus'] == 'authenticated':
                    if partner_id.country_id.phone_code and partner_id.mobile:
                        whatsapp_msg_number = partner_id.mobile
                        whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "");
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                            '+' + str(partner_id.country_id.phone_code), "")
                        phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get('whatsapp_token') + '&phone=' + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        phone_exists_response = requests.get(phone_exists_url)
                        json_response_phone_exists = json.loads(phone_exists_response.text)
                        if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and json_response_phone_exists['result'] == 'exists':
                            _logger.info("\nPartner phone exists")
                            url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                            headers = {"Content-Type": "application/json"}
                            html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))

                            if kwargs.get('email_from'):
                                if '<' in kwargs.get('email_from') and '>' in kwargs.get('email_from'):
                                    tmp_dict = {
                                        "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": self.convert_email_from_to_name(kwargs.get('email_from'))+''+ str(self.id) + ': '+ html_to_plain_text
                                    }
                                else:
                                    tmp_dict = {
                                        "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": kwargs.get('email_from')+ '' + str(self.id) + ': ' + html_to_plain_text
                                    }
                            else:
                                tmp_dict = {
                                    "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                    "body": html_to_plain_text
                                }
                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                            if response.status_code == 201 or response.status_code == 200:
                                _logger.info("\nSend Message successfully")
                                response_dict = response.json()
                                message_id.with_context({'from_odoobot': True}).write({'whatsapp_message_id': response_dict.get('id')})
                            if message_id.attachment_ids:
                                for attachment in message_id.attachment_ids:
                                    with open(attachment._full_path(attachment.store_fname), 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        # print(encoded_file)
                                        # print(encoded_file[2:-1])
                                        url_send_file = param.get(
                                            'whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+" + str(
                                                partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file,
                                                                           json.dumps(dict_send_file),
                                                                           headers=headers_send_file)
                                        # print(response_send_file.status_code)
                                        # print(response_send_file.content)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")
                        else:
                            invalid_whatsapp_number_partner.append(partner_id.name)
                    else:
                        no_phone_partners.append(partner_id.name)
                else:
                    raise UserError(_('Please authorize your mobile number with 1msg'))
            if len(invalid_whatsapp_number_partner) >= 1:
                raise UserError(_('Please add valid whatsapp number for %s customer')% ', '.join(invalid_whatsapp_number_partner))
        else:
            param = self.env['res.config.settings'].sudo().get_values()
            no_phone_partners = []
            invalid_whatsapp_number_partner = []
            for partner_id in partner_ids:
                if param.get('whatsapp_endpoint') and param.get('whatsapp_token'):
                    status_url = param.get('whatsapp_endpoint') + '/status?token=' + param.get('whatsapp_token')
                    status_response = requests.get(status_url)
                    json_response_status = json.loads(status_response.text)
                    if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
                        'accountStatus'] == 'authenticated':
                        if partner_id.country_id.phone_code and partner_id.mobile:
                            whatsapp_msg_number = partner_id.mobile
                            whatsapp_msg_number_without_space = whatsapp_msg_number.replace(" ", "")
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(partner_id.country_id.phone_code), "")
                            phone_exists_url = param.get('whatsapp_endpoint') + '/checkPhone?token=' + param.get(
                                'whatsapp_token') + '&phone=' + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                            phone_exists_response = requests.get(phone_exists_url)
                            json_response_phone_exists = json.loads(phone_exists_response.text)
                            if (phone_exists_response.status_code == 200 or phone_exists_response.status_code == 201) and \
                                    json_response_phone_exists['result'] == 'exists':
                                _logger.info("\nPartner phone exists")
                                url = param.get('whatsapp_endpoint') + '/sendMessage?token=' + param.get('whatsapp_token')
                                headers = {"Content-Type": "application/json"}
                                html_to_plain_text = self.custom_html2plaintext(kwargs.get('body'))
                                if kwargs.get('email_from'):
                                    if '<' in kwargs.get('email_from') and '>' in kwargs.get('email_from'):
                                        tmp_dict = {
                                            "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": self.convert_email_from_to_name(kwargs.get('email_from')) + '' + str(
                                                self.id) + ': ' + html_to_plain_text
                                        }
                                    else:
                                        tmp_dict = {
                                            "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": kwargs.get('email_from') + '' + str(self.id) + ': ' + html_to_plain_text
                                        }
                                else:
                                    tmp_dict = {
                                        "phone": "+" + str(partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                        "body": html_to_plain_text
                                    }
                                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                                if response.status_code == 201 or response.status_code == 200:
                                    _logger.info("\nSend Message successfully")
                                    response_dict = response.json()
                                    message_id.with_context({'from_odoobot': True}).write({'whatsapp_message_id': response_dict.get('id')})
                                if message_id.attachment_ids:
                                    Param = self.env['res.config.settings'].sudo().get_values()
                                    for attachment in message_id.attachment_ids:
                                        # with open(attachment._full_path(attachment.store_fname), 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        # print(encoded_file)
                                        # print(encoded_file[2:-1])
                                        url_send_file = param.get(
                                            'whatsapp_endpoint') + '/sendFile?token=' + param.get('whatsapp_token')
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": "+" + str(
                                                partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file,
                                                                           json.dumps(dict_send_file),
                                                                           headers=headers_send_file)
                                        # print(response_send_file.status_code)
                                        # print(response_send_file.content)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            _logger.info("\nSend file attachment successfully11")
                            else:
                                invalid_whatsapp_number_partner.append(partner_id.name)
                        else:
                            no_phone_partners.append(partner_id.name)
                    else:
                        raise UserError(_('Please authorize your mobile number with 1msg'))

        if len(invalid_whatsapp_number_partner) >= 1:
            raise UserError(
                _('Please add valid whatsapp number for %s customer') % ', '.join(invalid_whatsapp_number_partner))

    chat_partner = fields.Many2one('res.partner')
    whatsapp_meta_id = fields.Char("Meta ID")
    # attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_msg_res_partner_ir_attachments_rel', 'wizard_id', 'attachment_id', 'Attachments')
    channel_type = fields.Selection(selection_add=[("multi_livechat_NAMEs", "Whatsapp Chat")], ondelete={"multi_livechat_NAMEs": "cascade"})
