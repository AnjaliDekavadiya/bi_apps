import requests
import json
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class SendWAMessageMarketing(models.TransientModel):
    _name = 'whatsapp.msg.marketing'
    _description = 'Send WhatsApp Message'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_unique_user(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        return dbuuid + '_' + str(self.env.uid)

    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_msg_marketing_ir_attachments_rel', 'wizard_id', 'attachment_id', 'Attachments')
    unique_user = fields.Char(default=_default_unique_user)

    @api.model
    def default_get(self, fields):
        result = super(SendWAMessageMarketing, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        return result

    def action_send_msg_marketing(self):
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        whatsapp_instance_id = self.env['whatsapp.instance'].get_whatsapp_instance()
        if whatsapp_instance_id.provider == 'whatsapp_chat_api':
            if self.attachment_ids:
                self.with_context({'whatsapp_message': self.message, 'whatsapp_attachments': self.attachment_ids}).chat_api_send_whatsapp_message_from_contact(whatsapp_instance_id,
                                                                                                                                                               active_model, rec)
            else:
                self.with_context({'whatsapp_message': self.message}).chat_api_send_whatsapp_message_from_contact(whatsapp_instance_id, active_model, rec)

        elif whatsapp_instance_id.provider == 'gupshup':
            if self.attachment_ids:
                self.with_context({'whatsapp_message': self.message, 'whatsapp_attachments': self.attachment_ids}).gupshup_send_create_whatsapp_message(whatsapp_instance_id,
                                                                                                                                                        active_model, rec)
            else:
                self.with_context({'whatsapp_message': self.message}).gupshup_send_create_whatsapp_message(whatsapp_instance_id, active_model, rec)

    def chat_api_send_whatsapp_message_from_contact(self, whatsapp_instance_id, active_model, rec):
        status_url = whatsapp_instance_id.whatsapp_endpoint + '/status?token=' + whatsapp_instance_id.whatsapp_token
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)
        no_phone_partners = []
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status['accountStatus'] == 'authenticated':
            if active_model == 'whatsapp.contact':
                url = whatsapp_instance_id.whatsapp_endpoint + '/sendMessage?token=' + whatsapp_instance_id.whatsapp_token
                headers = {"Content-Type": "application/json"}
                tmp_dict = {"chatId": str(rec.whatsapp_id), "body": self.env.context.get('whatsapp_message')}
                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                if response.status_code == 201 or response.status_code == 200:
                    json_send_message_response = json.loads(response.text)
                    _logger.info("\nSend Message to contact successfully")
                    if not json_send_message_response.get('sent') and json_send_message_response.get('error') and json_send_message_response.get('error').get(
                            'message') == 'Recipient is not a valid WhatsApp user':
                        not_user = "not"
                        no_phone_partners.append(not_user)
                    elif json_send_message_response.get('sent'):
                        _logger.info("\nSend Message successfully")
                        self.marketing_create_whatsapp_message(rec.whatsapp_id, self.env.context.get('whatsapp_message'), json_send_message_response.get('id'),
                                                               json_send_message_response.get('message'),
                                                               "text",
                                                               whatsapp_instance_id, active_model, rec)
                if self.env.context.get('whatsapp_attachments'):
                    for attachment in self.env.context.get('whatsapp_attachments'):
                        with open("/tmp/" + attachment.name, 'wb') as tmp:
                            encoded_file = str(attachment.datas)
                            url_send_file = whatsapp_instance_id.whatsapp_endpoint + '/sendFile?token=' + whatsapp_instance_id.whatsapp_token
                            headers_send_file = {"Content-Type": "application/json"}
                            dict_send_file = {
                                "chatId": str(rec.whatsapp_id),
                                "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                "caption": attachment.name,
                                "filename": attachment.name
                            }
                            response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                            if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                _logger.info("\nSend file attachment successfully11")
                                json_send_file_response = json.loads(response_send_file.text)
                                self.marketing_create_whatsapp_message_for_attachment(rec.whatsapp_id, attachment, json_send_file_response.get('id'),
                                                                                      json_send_file_response.get('message'), attachment.mimetype,
                                                                                      whatsapp_instance_id, active_model, rec)

            if len(no_phone_partners) >= 1:
                raise UserError(_('Please add valid whatsapp number for %s customer') % ', '.join(no_phone_partners))
        else:
            raise UserError(_('Please authorize your mobile number with 1msg'))

    def gupshup_send_create_whatsapp_message(self, whatsapp_instance_id, active_model, record, res_partner_id=False):
        url = 'https://api.gupshup.io/sm/api/v1/msg'
        headers = {"Content-Type": "application/x-www-form-urlencoded", "apikey": whatsapp_instance_id.whatsapp_gupshup_api_key}
        payload = {}
        if active_model == 'whatsapp.contact':
            payload = {
                'channel': 'whatsapp',
                'source': whatsapp_instance_id.gupshup_source_number,
                'destination': record.whatsapp_id,
                'message': json.dumps({
                    'type': 'text',
                    'text': self.env.context.get('whatsapp_message')
                })
            }
        elif active_model == 'odoo.group':
            if self.env.context.get('whatsapp_contact_from_odoo_group'):
                payload = {
                    'channel': 'whatsapp',
                    'source': whatsapp_instance_id.gupshup_source_number,
                    'destination': record.whatsapp_id,
                    'message': json.dumps({
                        'type': 'text',
                        'text': self.env.context.get('whatsapp_message')
                    })
                }
            else:
                whatsapp_number = res_partner_id.mobile
                whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                whatsapp_msg_number_without_code = ''
                if '+' in whatsapp_msg_number_without_code:
                    whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(res_partner_id.country_id.phone_code), "")
                else:
                    whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(res_partner_id.country_id.phone_code), "")
                payload = {
                    'channel': 'whatsapp',
                    'source': whatsapp_instance_id.gupshup_source_number,
                    'destination': str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                    'message': json.dumps({
                        'type': 'text',
                        'text': self.env.context.get('whatsapp_message')
                    })
                }
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code in [202, 201, 200]:
            _logger.info("\nSend Message successfully from gupshup")
            response_dict = response.json()
            if active_model == 'whatsapp.contact':
                self.with_context({'partner_id': record.partner_id.id}).gupshup_marketing_create_whatsapp_message(record.whatsapp_id, self.env.context.get('whatsapp_message'), response_dict.get('messageId'), whatsapp_instance_id,
                                                           active_model, record)
            elif active_model == 'odoo.group':
                if self.env.context.get('whatsapp_contact_from_odoo_group'):
                    self.with_context({'partner_id': record.partner_id.id}).gupshup_marketing_create_whatsapp_message(record.whatsapp_id, self.env.context.get('whatsapp_message'),
                                                                                                                      response_dict.get('messageId'), whatsapp_instance_id,
                                                                                                                      active_model, record)
                else:
                    self.with_context({'partner_id': res_partner_id.id}).gupshup_marketing_create_whatsapp_message(str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code, self.env.context.get('whatsapp_message'),
                                                                                                                   response_dict.get('messageId'), whatsapp_instance_id,
                                                                                                                   active_model, record)
            if self.env.context.get('whatsapp_attachments'):
                for attachment_id in self.env.context.get('whatsapp_attachments'):
                    attachment_data = {}
                    if active_model == 'whatsapp.contact':
                        attachment_data = {
                            'channel': 'whatsapp',
                            'source': whatsapp_instance_id.gupshup_source_number,
                            'destination': record.whatsapp_id,
                        }
                    elif active_model == 'odoo.group':
                        if self.env.context.get('whatsapp_contact_from_odoo_group'):
                            attachment_data = {
                                'channel': 'whatsapp',
                                'source': whatsapp_instance_id.gupshup_source_number,
                                'destination': record.whatsapp_id,
                            }
                        else:
                            attachment_data = {
                                'channel': 'whatsapp',
                                'source': whatsapp_instance_id.gupshup_source_number,
                                'destination': str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                            }
                    attachment_data = self.env['whatsapp.msg.res.partner'].gupshup_create_attachment_dict_for_send_message(attachment_id, attachment_data)
                    response = requests.post(url, data=attachment_data, headers=headers)
                    if response.status_code in [202, 201, 200]:
                        _logger.info("\nSend Attachment successfully from gupshup")
                        response_dict = response.json()
                        if active_model == 'whatsapp.contact':
                            self.with_context({'partner_id': record.partner_id.id}).gupshup_marketing_create_whatsapp_message_for_attachment(record.whatsapp_id, attachment_id, response_dict.get('messageId'), attachment_id.mimetype,
                                                                                          whatsapp_instance_id, active_model, record)
                        elif active_model == 'odoo.group':
                            if self.env.context.get('whatsapp_contact_from_odoo_group'):
                                self.with_context({'partner_id': record.partner_id.id}).gupshup_marketing_create_whatsapp_message_for_attachment(record.whatsapp_id, attachment_id,
                                                                                                                                                 response_dict.get('messageId'),
                                                                                                                                                 attachment_id.mimetype,
                                                                                                                                                 whatsapp_instance_id, active_model,
                                                                                                                                                 record)
                            else:
                                self.with_context({'partner_id': res_partner_id.id}).gupshup_marketing_create_whatsapp_message_for_attachment(str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code, attachment_id,
                                                                                                                                                 response_dict.get('messageId'),
                                                                                                                                                 attachment_id.mimetype,
                                                                                                                                                 whatsapp_instance_id, active_model,
                                                                                                                                                 record)

    def marketing_create_whatsapp_message(self, mobile_with_country, message, message_id, chatId_message, type, whatsapp_instance_id, model, record):
        whatsapp_messages_dict = {
            'message_id': message_id,
            'name': message,
            'message_body': message,
            'fromMe': True,
            'to': mobile_with_country,
            'chatId': chatId_message[8:],
            'type': type,
            'chatName': chatId_message[8:-5],
            'time': fields.Datetime.now(),
            'state': 'sent',
            'whatsapp_instance_id': whatsapp_instance_id.id,
            'whatsapp_message_provider': whatsapp_instance_id.provider,
            'model': model,
            'res_id': record.id
        }

        if model == 'whatsapp.contact':
            whatsapp_messages_dict['partner_id'] = record.partner_id.id
            whatsapp_messages_dict['whatsapp_contact_id'] = record.id
        whatsapp_messages_id = self.env['whatsapp.messages'].sudo().create(whatsapp_messages_dict)
        _logger.info("Whatsapp message created in odoo %s: ", str(whatsapp_messages_id.id))

    def marketing_create_whatsapp_message_for_attachment(self, mobile_with_country, attachment_id, message_id, chatId_message, type, whatsapp_instance_id, model, record):
        whatsapp_messages_dict = {
            'message_id': message_id,
            'name': attachment_id.name,
            'message_body': attachment_id.name,
            'fromMe': True,
            'to': mobile_with_country,
            'chatId': chatId_message[8:],
            'type': type,
            'chatName': chatId_message[8:-5],
            'time': fields.Datetime.now(),
            'state': 'sent',
            'whatsapp_instance_id': whatsapp_instance_id.id,
            'whatsapp_message_provider': whatsapp_instance_id.provider,
            'model': model,
            'res_id': record.id,
            'attachment_id': attachment_id.id,
        }
        if model == 'whatsapp.contact':
            whatsapp_messages_dict['partner_id'] = record.partner_id.id
            whatsapp_messages_dict['whatsapp_contact_id'] = record.id
        whatsapp_messages_id = self.env['whatsapp.messages'].sudo().create(whatsapp_messages_dict)
        _logger.info("Whatsapp message created in odoo %s: ", str(whatsapp_messages_id.id))

    def gupshup_marketing_create_whatsapp_message(self, mobile_with_country, message, message_id, whatsapp_instance_id, model, record):
        whatsapp_messages_dict = {
            'message_id': message_id,
            'name': message,
            'message_body': message,
            'fromMe': True,
            'to': mobile_with_country,
            'type': type,
            'time': fields.Datetime.now(),
            'state': 'sent',
            'whatsapp_instance_id': whatsapp_instance_id.id,
            'whatsapp_message_provider': whatsapp_instance_id.provider,
            'model': model,
            'res_id': record.id,
            'senderName': whatsapp_instance_id.gupshup_source_number,
            'chatName': mobile_with_country,
        }
        if self._context.get('partner_id'):
            whatsapp_messages_dict['partner_id'] = self._context.get('partner_id')

        if model == 'whatsapp.contact':
            whatsapp_messages_dict['whatsapp_contact_id'] = record.id
        whatsapp_messages_id = self.env['whatsapp.messages'].sudo().create(whatsapp_messages_dict)
        _logger.info("Whatsapp message created in odoo from gupshup %s: ", str(whatsapp_messages_id.id))

    def gupshup_marketing_create_whatsapp_message_for_attachment(self, mobile_with_country, attachment_id, message_id, type, whatsapp_instance_id, model, record):
        whatsapp_messages_dict = {
            'message_id': message_id,
            'name': attachment_id.name,
            'message_body': attachment_id.name,
            'fromMe': True,
            'to': mobile_with_country,
            'type': type,
            'time': fields.Datetime.now(),
            'state': 'sent',
            'whatsapp_instance_id': whatsapp_instance_id.id,
            'whatsapp_message_provider': whatsapp_instance_id.provider,
            'model': model,
            'res_id': record.id,
            'attachment_id': attachment_id.id,
            'senderName': whatsapp_instance_id.gupshup_source_number,
            'chatName': mobile_with_country,
        }
        if self._context.get('partner_id'):
            whatsapp_messages_dict['partner_id'] = self._context.get('partner_id')
        if model == 'whatsapp.contact':
            whatsapp_messages_dict['whatsapp_contact_id'] = record.id
        whatsapp_messages_id = self.env['whatsapp.messages'].sudo().create(whatsapp_messages_dict)
        _logger.info("Whatsapp message created in odoo from gupshup %s: ", str(whatsapp_messages_id.id))
