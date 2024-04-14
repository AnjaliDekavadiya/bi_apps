import logging
import json
import requests
import phonenumbers
from odoo.exceptions import UserError
from odoo import api, fields, models, _

logger = logging.getLogger(__name__)
from odoo.addons.phone_validation.tools import phone_validation
from ...pragtech_whatsapp_base.controller.main import WhatsappBase


class whatsapp_contact(models.Model):
    _name = 'whatsapp.contact'
    _description = 'Whatsapp Contact'

    name = fields.Char('Name')
    mobile = fields.Char('Mobile')
    whatsapp_id = fields.Char('Whatsapp id')
    partner_id = fields.Many2one('res.partner', 'Partner', domain="[('mobile', '!=', False), ('country_id', '!=', False)]")
    odoo_group_id = fields.Many2many('odoo.group', column1='whatsapp_contact_ids', column2='odoo_group_id', string='Odoo Group')
    active = fields.Boolean('Active', default=True)
    whatsapp_msg_ids = fields.One2many('whatsapp.messages', 'whatsapp_contact_id', 'WhatsApp Messages')
    chatId = fields.Char('Chat ID')
    sanitized_mobile = fields.Char('Sanitized Mobile')
    whatsapp_instance_id = fields.Many2one('whatsapp.instance', string='WhatsApp Instance')

    @api.model
    def create(self, vals):
        res = super(whatsapp_contact, self).create(vals)
        return res

    def _get_whatsapp_contacts(self):
        whatsapp_instance_id = self.env['whatsapp.instance'].get_whatsapp_instance()
        if whatsapp_instance_id.provider == 'whatsapp_chat_api':
            self.chat_api_get_create_whatsapp_contact(whatsapp_instance_id)
        elif whatsapp_instance_id.provider == 'gupshup':
            self.gupshup_create_whatsapp_contact(whatsapp_instance_id)

    def chat_api_get_create_whatsapp_contact(self, whatsapp_instance_id):
        status_url = whatsapp_instance_id.whatsapp_endpoint + '/status?token=' + whatsapp_instance_id.whatsapp_token
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status.get('accountStatus') == 'authenticated':
            contact_url = whatsapp_instance_id.whatsapp_endpoint + '/dialogs?token=' + whatsapp_instance_id.whatsapp_token
            contact_response = requests.get(contact_url)
            contact_json_response = json.loads(contact_response.text)
            if contact_json_response:
                for dialog_dict in contact_json_response['dialogs']:
                    whatsapp_contact_dict = {}
                    if '@c.us' in dialog_dict['chatId']:
                        if dialog_dict['chatId']:
                            whatsapp_contact_dict['whatsapp_id'] = dialog_dict['chatId']
                            whatsapp_contact_dict['mobile'] = (dialog_dict['chatId'])[:-5]
                            mobile = "+" + whatsapp_contact_dict['mobile']
                        if dialog_dict['name']:
                            whatsapp_contact_dict['name'] = dialog_dict['name']
                        chatid_split = dialog_dict.get('chatId').split('@')
                        mobile = '+' + chatid_split[0]
                        try:
                            mobile_country_code = phonenumbers.parse(mobile, None)
                        except phonenumbers.phonenumberutil.NumberParseException:
                            # Skip invalid phone numbers
                            continue
                        mobile_number = mobile_country_code.national_number
                        res_country_id = self.env['res.country'].sudo().search([('phone_code', '=', mobile_country_code.country_code)], limit=1)
                        try:
                            reg_sanitized_number = phone_validation.phone_format(str(mobile_number), res_country_id.code, mobile_country_code.country_code)
                        except Exception as e:
                            logger.info("Invalid mobile number: " + str(mobile_number))
                            continue
                        res_partner_id = self.env['res.partner'].sudo().search(['|', ('mobile', '=', reg_sanitized_number), ('chatId', '=', dialog_dict['chatId'])], limit=1)
                        whatsapp_contact_dict['sanitized_mobile'] = reg_sanitized_number
                        if res_partner_id:
                            whatsapp_contact_dict['partner_id'] = res_partner_id.id
                        else:
                            country_with_mobile = WhatsappBase.sanitized_country_mobile_from_chat_id(self, dialog_dict.get('chatId'))
                            res_partner_id = WhatsappBase.create_res_partner_against_whatsapp(self, dialog_dict.get('chatId'), dialog_dict.get('name'), country_with_mobile[0],
                                                                                              country_with_mobile[1])
                            whatsapp_contact_dict['partner_id'] = res_partner_id
                        whatsapp_contact_dict['whatsapp_instance_id'] = whatsapp_instance_id.id
                        if whatsapp_contact_dict:
                            whatsapp_contact = self.sudo().search([('whatsapp_id', '=', whatsapp_contact_dict['whatsapp_id'])])
                            if whatsapp_contact:
                                whatsapp_contact_write_record = whatsapp_contact.sudo().write(whatsapp_contact_dict)
                                logger.info("Whatsapp Contact is updated in odoo----------- " + str(whatsapp_contact.whatsapp_id))

                            else:
                                whatsapp_contact_create_record = self.sudo().create(whatsapp_contact_dict)
                                logger.info("Whatsapp Contact is created in odoo----------- " + str(whatsapp_contact_create_record.id))
        else:
            raise UserError(_('Please authorize your mobile number with 1msg'))

    def gupshup_create_whatsapp_contact(self, whatsapp_instance_id):
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "apikey": whatsapp_instance_id.whatsapp_gupshup_api_key}
        url = "https://api.gupshup.io/sm/api/v1/users/" + whatsapp_instance_id.whatsapp_gupshup_app_name
        response = requests.get(url, headers=headers)
        if response.status_code in [202, 201, 200]:
            contact_json_response = json.loads(response.text)

            for user_dict in contact_json_response.get('users'):
                whatsapp_contact_dict = {}
                whatsapp_contact_dict['whatsapp_id'] = user_dict.get('countryCode') + user_dict.get('phoneCode')
                mobile = '+' + user_dict.get('countryCode') + user_dict.get('phoneCode')
                try:
                    mobile_country_code = phonenumbers.parse(mobile, None)
                except phonenumbers.phonenumberutil.NumberParseException:
                    # Skip invalid phone numbers
                    continue
                mobile_number = mobile_country_code.national_number
                res_country_id = self.env['res.country'].sudo().search(
                    [('phone_code', '=', mobile_country_code.country_code)], limit=1)
                country_with_mobile = WhatsappBase.sanitized_country_mobile_from_chat_id(self, mobile)
                try:
                    reg_sanitized_number = phone_validation.phone_format(str(mobile_number), res_country_id.code,
                                                                         mobile_country_code.country_code)
                except Exception as e:
                    logger.info("Invalid mobile number: " + str(mobile_number))
                    continue
                res_partner_id = self.env['res.partner'].sudo().search(['|',('mobile', '=', reg_sanitized_number), ('chatId', '=', mobile)], limit=1)
                whatsapp_contact_dict['sanitized_mobile'] = reg_sanitized_number
                if res_partner_id:
                    whatsapp_contact_dict['partner_id'] = res_partner_id.id
                else:
                    res_partner_id = WhatsappBase.create_res_partner_against_whatsapp(self, mobile, user_dict.get(
                        'countryCode') + user_dict.get('phoneCode'),country_with_mobile[0],country_with_mobile[1])
                    whatsapp_contact_dict['partner_id'] = res_partner_id
                    res_partner_id = self.env['res.partner'].sudo().search([('id', '=', res_partner_id)], limit=1)

                whatsapp_contact_dict['name'] = res_partner_id.name
                whatsapp_contact_dict['whatsapp_instance_id'] = whatsapp_instance_id.id
                if whatsapp_contact_dict:
                    whatsapp_contact = self.sudo().search([('whatsapp_id', '=', whatsapp_contact_dict['whatsapp_id'])])
                    if whatsapp_contact:
                        whatsapp_contact.sudo().write(whatsapp_contact_dict)
                        logger.info("Write into existing Odoo whatsapp contact from gupshup----------- " + str(
                            whatsapp_contact.whatsapp_id))

                    else:
                        whatsapp_contact_create_record = self.sudo().create(whatsapp_contact_dict)
                        logger.info("Create into existing Odoo whatsapp contact from gupshup----------- " + str(
                            whatsapp_contact_create_record.id))

    def _sms_get_default_partners(self):
        """ Override of mail.thread method.
            SMS recipients on partners are the partners themselves.
        """
        return self


class whatsapp_contact_target(models.Model):
    _name = 'whatsapp.contact.list.action'
    _description = 'Whatsapp Contact List Action'

    contact_ids = fields.Many2many('whatsapp.contact', 'whatsapp_contact_whatsapp_contact_target_rel', 'wizard_id', 'contact_id',
                                   'Whatsapp Contacts')
    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_contact_ir_attachments_rel', 'wizard_id', 'attachment_id', 'Attachments')

    def _get_records(self, model):
        if self.env.context.get('active_ids'):
            records = model.browse(self.env.context.get('active_ids', []))
        else:
            records = model.browse(self.env.context.get('active_id', []))
        return records

    @api.model
    def default_get(self, fields):
        result = super(whatsapp_contact_target, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        model = self.env[active_model]
        records = self.env['whatsapp.contact.list.action']._get_records(model)
        result['contact_ids'] = [(6, 0, records.ids)]
        return result

    def action_whatsapp_group_list(self):
        active_model = self.env.context.get('active_model')
        res_ids = self.env.context.get('active_ids')
        for res_id in res_ids:
            record = self.env[active_model].browse(res_id)
            whatsapp_instance_id = self.env['whatsapp.instance'].get_whatsapp_instance()
            if whatsapp_instance_id.provider == 'whatsapp_chat_api':
                if self.attachment_ids:
                    self.env['whatsapp.msg.marketing'].with_context({'whatsapp_message': self.message, 'whatsapp_attachments': self.attachment_ids}).chat_api_send_whatsapp_message_from_contact(whatsapp_instance_id,
                                                                                                                                                    active_model, record)
                else:
                    self.env['whatsapp.msg.marketing'].with_context({'whatsapp_message': self.message}).chat_api_send_whatsapp_message_from_contact(whatsapp_instance_id,
                                                                                                                                                    active_model, record)

            elif whatsapp_instance_id.provider == 'gupshup':
                if self.attachment_ids:
                    self.env['whatsapp.msg.marketing'].with_context(
                        {'whatsapp_message': self.message, 'whatsapp_attachments': self.attachment_ids}).gupshup_send_create_whatsapp_message(whatsapp_instance_id, active_model,
                                                                                                                                              record)
                else:
                    self.env['whatsapp.msg.marketing'].with_context({'whatsapp_message': self.message}).gupshup_send_create_whatsapp_message(whatsapp_instance_id, active_model,
                                                                                                                                             record)
