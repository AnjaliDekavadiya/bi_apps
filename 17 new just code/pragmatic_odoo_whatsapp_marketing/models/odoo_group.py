import logging
import json
import requests
from odoo import api, fields, models, _
from requests.structures import CaseInsensitiveDict
from datetime import datetime


_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class odooGroup(models.Model):
    _name = 'odoo.group'
    _description = 'Odoo Group'

    name = fields.Char('Name', required=True)
    active = fields.Boolean("Active", default=True)
    partner_ids = fields.Many2many(
        'res.partner', 'odoo_group_res_partner_rel',
        'wizard_id', 'partner_id', 'Associated Partner', domain="[('mobile', '!=', False), ('country_id', '!=', False)]")
    whatsapp_contact_ids = fields.Many2many('whatsapp.contact', column1='odoo_group_id', column2='whatsapp_contact_ids', string='Whatsapp Contact')
    odoo_group_id = fields.Char('Group Id')


class odoo_group_form(models.Model):
    _name = 'odoo.group.form'
    _description = 'Whatsapp Contact List Action'

    contact_ids = fields.Many2many(
        'odoo.group', 'odoo_group_odoo_group_form_action_rel',
        'wizard_id', 'odoo_group_id', 'Associated Partner')
    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'odoo_group_form_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')

    def action_send_msg_odoo_group(self):
        whatsapp_instance_id = self.env['whatsapp.instance'].get_whatsapp_instance()
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        if whatsapp_instance_id.provider == 'whatsapp_chat_api':
            if self.attachment_ids:
                self.with_context({'whatsapp_message': self.message, 'whatsapp_attachments': self.attachment_ids}).chat_api_send_whatsapp_message_from_odoo_group(
                    whatsapp_instance_id, active_model, rec)
            else:
                self.with_context({'whatsapp_message': self.message}).chat_api_send_whatsapp_message_from_odoo_group(whatsapp_instance_id, active_model, rec)
        elif whatsapp_instance_id.provider == "meta":
            active_model = self.env.context.get('active_model')
            res_id = self.env.context.get('active_id')
            rec = self.env[active_model].browse(res_id)
            message_vals = self.sudo().search([], order='id desc', limit=1)
            message = message_vals.message
            file_data = message_vals.attachment_ids
            # phone_number = self.env['crm.lead'].sudo().search([], order='id desc', limit=1)
            config_settings = self.env['whatsapp.instance'].sudo().search([('status','!=','disable')], limit=1)
            token = config_settings.whatsapp_meta_api_token
            if token:
                for partner in rec.partner_ids:
                    number = partner.mobile
                    whatsapp_msg_number_without_space = number.replace(" ", "")
                    whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                        '+' + str(partner.country_id.phone_code), "")
                    number = str(
                        partner.country_id.phone_code) + whatsapp_msg_number_without_code
                    res_partner_objs = self.env['res.partner'].sudo().search([('chatId', '=', number)])
                    number_id = config_settings.whatsapp_meta_phone_number_id
                    url = "https://graph.facebook.com/v16.0/{}/messages".format(number_id)
                    req_headers = CaseInsensitiveDict()
                    req_headers["Authorization"] = "Bearer " + token
                    req_headers["Content-Type"] = "application/json"
                    data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": number,
                                "type": "text",
                                "text": {
                                    "body": message,
                                }
                            }
                    if data_json.get('text'):
                        vals = {
                            'message_body': message,
                            'senderName': res_partner_objs.name,
                            'state': 'sent',
                            # 'to': whatsapp_msg_source_number,
                            'partner_id': res_partner_objs.id,
                            'time': datetime.today(),
                            'type': 'text',
                            'chatId': res_partner_objs.chatId,
                            # 'attachment_id': file_data.name
                        }
                    if file_data:
                        for attachment in file_data:
                            data_json = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": number,
                                "type": "image",
                                "image": {
                                    "link": attachment.public_url,
                                    "caption": message
                                }
                            }
                            if data_json.get('image'):
                                vals = {
                                    'message_body': message,
                                    'senderName': res_partner_objs.name,
                                    'state': 'sent',
                                    # 'to': whatsapp_msg_source_number,
                                    'partner_id': res_partner_objs.id,
                                    'time': datetime.today(),
                                    'type': 'image',
                                    'chatId': res_partner_objs.chatId,
                                    'attachment_id': file_data.id
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
                                    "caption": message
                                }
                            }
                            if data_json.get('document'):
                                vals = {
                                    'message_body': message,
                                    'senderName': res_partner_objs.name,
                                    'state': 'sent',
                                    # 'to': whatsapp_msg_source_number,
                                    'partner_id': res_partner_objs.id,
                                    'time': datetime.today(),
                                    'type': 'document',
                                    'chatId': res_partner_objs.chatId,
                                    'attachment_id': file_data.id
                                }
                    message_cr = self.env['whatsapp.messages'].sudo().create(vals)
                    response = requests.post(url, headers=req_headers, json=data_json)
                    if response.status_code in [202, 201, 200]:
                        _logger.info("\nSend Message successfully")
        elif whatsapp_instance_id.provider == 'gupshup':
            if self.attachment_ids:
                self.with_context({'whatsapp_message': self.message, 'whatsapp_attachments': self.attachment_ids, 'active_model': active_model}).gupshup_send_whatsapp_message_from_odoo_group(whatsapp_instance_id, rec)
            else:
                self.with_context({'whatsapp_message': self.message, 'active_model': active_model}).gupshup_send_whatsapp_message_from_odoo_group(whatsapp_instance_id, rec)


    def chat_api_send_whatsapp_message_from_odoo_group(self, whatsapp_instance_id, active_model, rec):
        status_url = whatsapp_instance_id.whatsapp_endpoint + '/status?token=' + whatsapp_instance_id.whatsapp_token
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status.get(
                'accountStatus') == 'authenticated' and active_model == 'odoo.group':
            for res_partner_id in rec.partner_ids:
                if rec.whatsapp_contact_ids:
                    for contact_id in rec.whatsapp_contact_ids:
                        if contact_id.sanitized_mobile != res_partner_id.mobile:
                            whatsapp_number = res_partner_id.mobile
                            whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                            whatsapp_msg_number_without_code = ''
                            if '+' in whatsapp_msg_number_without_code:
                                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(res_partner_id.country_id.phone_code), "")
                            else:
                                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(res_partner_id.country_id.phone_code), "")
                            url = whatsapp_instance_id.whatsapp_endpoint + '/sendMessage?token=' + whatsapp_instance_id.whatsapp_token
                            headers = {"Content-Type": "application/json"}
                            tmp_dict = {
                                "phone": str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                "body": self.env.context.get('whatsapp_message')
                            }
                            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                            if response.status_code == 201 or response.status_code == 200:
                                json_send_message_response = json.loads(response.text)
                                if json_send_message_response.get('sent'):
                                    _logger.info("\nSend Message successfully")
                                    number_with_code = str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                                    self.env['whatsapp.msg'].create_whatsapp_message(number_with_code, self.env.context.get('whatsapp_message'),
                                                                                     json_send_message_response.get('id'),
                                                                                     json_send_message_response.get('message'), "text",
                                                                                     whatsapp_instance_id, active_model, rec)
                            if self.env.context.get('whatsapp_attachments'):
                                for attachment in self.env.context.get('whatsapp_attachments'):
                                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                                        encoded_file = str(attachment.datas)
                                        url_send_file = whatsapp_instance_id.whatsapp_endpoint + '/sendFile?token=' + whatsapp_instance_id.whatsapp_token
                                        headers_send_file = {"Content-Type": "application/json"}
                                        dict_send_file = {
                                            "phone": str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                                            "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                            "filename": attachment.name
                                        }
                                        response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                            json_send_message_response = json.loads(response_send_file.text)
                                            if json_send_message_response.get('sent'):
                                                _logger.info("\nSend file attachment successfully11")
                                                number_with_code = str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code

                                                self.env['whatsapp.msg'].create_whatsapp_message_for_attachment(number_with_code, attachment, json_send_message_response.get('id'),
                                                                                                                json_send_message_response.get('message'), attachment.mimetype,
                                                                                                                whatsapp_instance_id, active_model, rec)
                elif not rec.whatsapp_contact_ids:
                    whatsapp_number = res_partner_id.mobile
                    whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                    whatsapp_msg_number_without_code = ''
                    if '+' in whatsapp_msg_number_without_space:
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                        '+' + str(res_partner_id.country_id.phone_code), "")
                    else:
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(res_partner_id.country_id.phone_code), "")
                    url = whatsapp_instance_id.whatsapp_endpoint + '/sendMessage?token=' + whatsapp_instance_id.whatsapp_token
                    headers = {"Content-Type": "application/json"}
                    tmp_dict = {
                        "phone": str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code,
                        "body": self.message}
                    response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                    if response.status_code == 201 or response.status_code == 200:
                        json_send_message_response = json.loads(response.text)
                        if json_send_message_response.get('sent'):
                            _logger.info("\nSend Message successfully")
                            number_with_code = str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                            self.env['whatsapp.msg'].create_whatsapp_message(number_with_code, self.message, json_send_message_response.get('id'),
                                                                             json_send_message_response.get('message'), "text",
                                                                             whatsapp_instance_id, active_model, rec)

                    if self.env.context.get('whatsapp_attachments'):
                        for attachment in self.env.context.get('whatsapp_attachments'):
                            with open("/tmp/" + attachment.name, 'wb') as tmp:
                                encoded_file = str(attachment.datas)
                                url_send_file = whatsapp_instance_id.whatsapp_endpoint + '/sendFile?token=' + whatsapp_instance_id.whatsapp_token
                                headers_send_file = {"Content-Type": "application/json"}
                                number_with_code = str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                                dict_send_file = {
                                    "phone": number_with_code,
                                    "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                    "filename": attachment.name
                                }
                                response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                                if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                    _logger.info("\nSend file attachment successfully11")
                                    json_send_file_response = json.loads(response_send_file.text)
                                    self.env['whatsapp.msg'].create_whatsapp_message_for_attachment(number_with_code, attachment, json_send_file_response.get('id'),
                                                                                                    json_send_file_response.get('message'), attachment.mimetype,
                                                                                                    whatsapp_instance_id, active_model, rec)
            for contact_id in rec.whatsapp_contact_ids:
                url = whatsapp_instance_id.whatsapp_endpoint + '/sendMessage?token=' + whatsapp_instance_id.whatsapp_token
                headers = {"Content-Type": "application/json"}
                tmp_dict = {
                    "chatId": str(contact_id.whatsapp_id),
                    "body": self.message}
                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                if response.status_code == 201 or response.status_code == 200:
                    json_send_message_response = json.loads(response.text)
                    if json_send_message_response.get('sent'):
                        _logger.info("\nSend Message successfully")
                        self.env['whatsapp.msg'].create_whatsapp_message(str(contact_id.whatsapp_id), self.message, json_send_message_response.get('id'),
                                                                         json_send_message_response.get('message'), "text",
                                                                         whatsapp_instance_id, active_model, rec)
                if self.attachment_ids:
                    for attachment in self.attachment_ids:
                        with open("/tmp/" + attachment.name, 'wb') as tmp:
                            encoded_file = str(attachment.datas)
                            url_send_file = whatsapp_instance_id.whatsapp_endpoint + '/sendFile?token=' + whatsapp_instance_id.whatsapp_token
                            headers_send_file = {"Content-Type": "application/json"}
                            number_with_code = str(contact_id.whatsapp_id)
                            dict_send_file = {
                                "chatId": str(contact_id.whatsapp_id),
                                "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                "filename": attachment.name
                            }
                            response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                            if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                _logger.info("\nSend file attachment successfully11")
                                json_send_file_response = json.loads(response_send_file.text)

                                self.env['whatsapp.msg'].create_whatsapp_message_for_attachment(number_with_code, attachment, json_send_file_response.get('id'),
                                                                                                json_send_file_response.get('message'), attachment.mimetype,
                                                                                                whatsapp_instance_id, active_model, rec)

    def gupshup_send_whatsapp_message_from_odoo_group(self, whatsapp_instance_id, record):
        print("\n=======self.env.context.get('whatsapp_attachments')===2==",
              self.env.context.get('whatsapp_attachments'))
        active_model = self.env.context.get('active_model')
        for res_partner_id in record.partner_ids:
            if record.whatsapp_contact_ids:
                for contact_id in record.whatsapp_contact_ids:
                    if contact_id.sanitized_mobile != res_partner_id.mobile:
                        self.env['whatsapp.msg.marketing'].with_context({'whatsapp_message': self.message}).gupshup_send_create_whatsapp_message(whatsapp_instance_id, active_model, record, res_partner_id)
            elif not record.whatsapp_contact_ids:
                if self.env.context.get('whatsapp_attachments'):
                    self.env['whatsapp.msg.marketing'].with_context({'whatsapp_message': self.env.context.get('whatsapp_message'), 'whatsapp_attachments': self.env.context.get('whatsapp_attachments')}).gupshup_send_create_whatsapp_message(whatsapp_instance_id, active_model, record, res_partner_id)
                else:
                    self.env['whatsapp.msg.marketing'].with_context({'whatsapp_message': self.env.context.get('whatsapp_message')}).gupshup_send_create_whatsapp_message(whatsapp_instance_id, active_model, record, res_partner_id)

        for contact_id in record.whatsapp_contact_ids:
            if self.env.context.get('whatsapp_attachments'):
                self.env['whatsapp.msg.marketing'].with_context({'whatsapp_message': self.env.context.get('whatsapp_message'), 'whatsapp_attachments': self.env.context.get('whatsapp_attachments'), 'whatsapp_contact_from_odoo_group': True}).gupshup_send_create_whatsapp_message(whatsapp_instance_id, active_model,
                                                                                                                                                 contact_id)
            else:
                self.env['whatsapp.msg.marketing'].with_context({'whatsapp_message': self.env.context.get('whatsapp_message'), 'whatsapp_contact_from_odoo_group': True}).gupshup_send_create_whatsapp_message(whatsapp_instance_id, active_model,
                                                                                                                                                 contact_id)


class odoo_group_target(models.Model):
    _name = 'odoo.group.list.action'
    _description = 'Whatsapp Contact List Action'

    contact_ids = fields.Many2many(
        'odoo.group', 'odoo_group_odoo_group_list_action_rel',
        'wizard_id', 'odoo_group_id', 'Associated Partner')
    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'odoo_group_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')

    def _get_records(self, model):
        if self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    @api.model
    def default_get(self, fields):
        result = super(odoo_group_target, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        model = self.env[active_model]
        records = self.env['whatsapp.contact.list.action']._get_records(model)
        result['contact_ids'] = [(6, 0, records.ids)]
        return result

    def action_odoo_group_list(self):
        whatsapp_instance_id = self.env['whatsapp.instance'].get_whatsapp_instance()
        active_model = self.env.context.get('active_model')
        res_ids = self.env.context.get('active_ids')
        for res_id in res_ids:
            rec = self.env[active_model].browse(res_id)
            if whatsapp_instance_id.provider == 'whatsapp_chat_api':
                if self.attachment_ids:
                    self.env['odoo.group.form'].with_context(
                        {'whatsapp_message': self.message, 'whatsapp_attachments': self.attachment_ids}).chat_api_send_whatsapp_message_from_odoo_group(
                        whatsapp_instance_id, active_model, rec)
                else:
                    self.env['odoo.group.form'].with_context({'whatsapp_message': self.message}).chat_api_send_whatsapp_message_from_odoo_group(whatsapp_instance_id, active_model,
                                                                                                                                                rec)
            elif whatsapp_instance_id.provider == 'gupshup':
                if self.attachment_ids:
                    self.env['odoo.group.form'].with_context(
                        {'whatsapp_message': self.message, 'whatsapp_attachments': self.attachment_ids, 'active_model': active_model}).gupshup_send_whatsapp_message_from_odoo_group(whatsapp_instance_id, rec)
                else:
                    self.env['odoo.group.form'].with_context({'whatsapp_message': self.message, 'active_model': active_model}).gupshup_send_whatsapp_message_from_odoo_group(whatsapp_instance_id, rec)
            elif whatsapp_instance_id.provider == "meta":
                active_model = self.env.context.get('active_model')
                res_id = self.env.context.get('active_id')
                rec = self.env[active_model].browse(res_id)
                message_vals = self.sudo().search([], order='id desc', limit=1)
                message = message_vals.message
                file_data = message_vals.attachment_ids
                # phone_number = self.env['crm.lead'].sudo().search([], order='id desc', limit=1)
                config_settings = self.env['whatsapp.instance'].sudo().search([('status', '!=', 'disable')], limit=1)
                token = config_settings.whatsapp_meta_api_token
                if token:
                    for partner in rec.partner_ids:
                        number = partner.mobile
                        whatsapp_msg_number_without_space = number.replace(" ", "")
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                            '+' + str(partner.country_id.phone_code), "")
                        number = str(
                            partner.country_id.phone_code) + whatsapp_msg_number_without_code
                        whatsapp_msg_number_without_space = number.replace(" ", "")
                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                            '+' + str(partner.country_id.phone_code), "")
                        number = str(
                            partner.country_id.phone_code) + whatsapp_msg_number_without_code
                        res_partner_objs = self.env['res.partner'].sudo().search([('chatId', '=', number)])
                        number_id = config_settings.whatsapp_meta_phone_number_id
                        url = "https://graph.facebook.com/v16.0/{}/messages".format(number_id)
                        req_headers = CaseInsensitiveDict()
                        req_headers["Authorization"] = "Bearer " + token
                        req_headers["Content-Type"] = "application/json"
                        data_json = {
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": number,
                            "type": "text",
                            "text": {
                                "body": message,
                            }
                        }
                        if data_json.get('text'):
                            vals = {
                                'message_body': message,
                                'senderName': res_partner_objs.name,
                                'state': 'sent',
                                # 'to': whatsapp_msg_source_number,
                                'partner_id': res_partner_objs.id,
                                'time': datetime.today(),
                                'type': 'text',
                                'chatId': res_partner_objs.chatId,
                                # 'attachment_id': file_data.name
                            }
                        if file_data:
                            for attachment in file_data:
                                data_json = {
                                    "messaging_product": "whatsapp",
                                    "recipient_type": "individual",
                                    "to": number,
                                    "type": "image",
                                    "image": {
                                        "link": attachment.public_url,
                                        "caption": message
                                    }
                                }
                                if data_json.get('image'):
                                    vals = {
                                        'message_body': message,
                                        'senderName': res_partner_objs.name,
                                        'state': 'sent',
                                        # 'to': whatsapp_msg_source_number,
                                        'partner_id': res_partner_objs.id,
                                        'time': datetime.today(),
                                        'type': 'image',
                                        'chatId': res_partner_objs.chatId,
                                        'attachment_id': file_data.id
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
                                        "caption": message
                                    }
                                }
                                if data_json.get('document'):
                                    vals = {
                                        'message_body': message,
                                        'senderName': res_partner_objs.name,
                                        'state': 'sent',
                                        # 'to': whatsapp_msg_source_number,
                                        'partner_id': res_partner_objs.id,
                                        'time': datetime.today(),
                                        'type': 'document',
                                        'chatId': res_partner_objs.chatId,
                                        'attachment_id': file_data.id
                                    }
                        message_cr = self.env['whatsapp.messages'].sudo().create(vals)
                        response = requests.post(url, headers=req_headers, json=data_json)
                        if response.status_code in [202, 201, 200]:
                            _logger.info("\nSend Message successfully")
