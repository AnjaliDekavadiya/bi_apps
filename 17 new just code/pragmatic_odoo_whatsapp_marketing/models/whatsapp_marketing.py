import logging
import requests
import json
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from requests.structures import CaseInsensitiveDict

_logger = logging.getLogger(__name__)
WHATSAPP_BUSINESS_MODELS = [
    'crm.lead',
    'event.registration',
    'hr.applicant',
    'res.partner',
    'event.track',
    'sale.order',
    'odoo.group',
    'whatsapp.contact'
]


class whatsapp_marketing(models.Model):
    _name = 'whatsapp.marketing'
    _inherit = ['mail.render.mixin']
    _description = 'Whatsapp Message'

    name = fields.Char(string="Name")
    whatsapp_templates_id = fields.Many2one('whatsapp.templates', string='WhatsApp Template')
    whatsapp_model_id = fields.Many2one('ir.model', string='Recipients', ondelete='cascade', required=True,
                                        domain=[('model', 'in', WHATSAPP_BUSINESS_MODELS)],
                                        default=lambda self: self.env.ref('pragmatic_odoo_whatsapp_marketing.model_odoo_group').id)
    whatsapp_model_real = fields.Char(string='Recipients Real Model', compute='_compute_model')
    whatsapp_model_name = fields.Char(
        string='Recipients Model Name', related='whatsapp_model_id.model',
        readonly=True, related_sudo=True)
    whatsapp_domain = fields.Char(
        string='Domain', compute='_compute_whatsapp_domain',
        readonly=False, store=True)
    message_type = fields.Selection([('message', 'Message')], string="Message Type", default="message", required=True)
    message_body = fields.Text('Body', required=True)
    body_html = fields.Html(string='Body converted to be sent by mail', sanitize_attributes=False)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    # attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_marketing_ir_attachments_rel',
    #                                   'whatsapp_message_id', 'attachment_id', string='Attachments')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    campaign_id = fields.Many2one('utm.campaign', string='UTM Campaign', index=True)
    source_id = fields.Char()
    odoo_group_ids = fields.Many2many('odoo.group', 'whatsapp_marketing_odoo_group_rel', string='Whatsapp Message')
    state = fields.Selection([('draft', 'Draft'), ('in_queue', 'In Queue'), ('done', 'Sent')],
                             string='Status', required=True, copy=False, default='draft')
    schedule_date = fields.Datetime(string='Scheduled for')
    next_departure = fields.Datetime(compute="_whatsapp_compute_next_departure", string='Scheduled date')
    sent_date = fields.Datetime(string='Sent Date', copy=False)
    whatsapp_instance_id = fields.Many2one('whatsapp.instance', string='WhatsApp Instance')
    whatsapp_template_id = fields.Many2one('whatsapp.templates', string='WhatsApp Template', domain="[('marketing_template', '=', True)]")
    whatsapp_provider = fields.Selection(related='whatsapp_instance_id.provider', string='Whatsapp Provider')

    model_object_field = fields.Many2one(
        'ir.model.fields', string="Field", store=False,
        help="Select target field from the related document model.\n"
             "If it is a relationship field you will be able to select "
             "a target field at the destination of the relationship.")
    sub_object = fields.Many2one(
        'ir.model', 'Sub-model', readonly=True, store=False,
        help="When a relationship field is selected as first field, "
             "this field shows the document model the relationship goes to.")
    sub_model_object_field = fields.Many2one(
        'ir.model.fields', 'Sub-field', store=False,
        help="When a relationship field is selected as first field, "
             "this field lets you select the target field within the "
             "destination document model (sub-model).")
    null_value = fields.Char('Default Value', store=False, help="Optional value to use if the target field is empty")
    copyvalue = fields.Char(
        'Placeholder Expression', store=False,
        help="Final placeholder expression, to be copy-pasted in the desired template field.")



    @api.model
    def create(self, vals):
        if vals.get('name'):
            self.validation_of_name(vals.get('name'))
        return super(whatsapp_marketing, self).create(vals)

    def write(self, vals):
        if vals.get('name'):
            self.validation_of_name(vals.get('name'))
        return super(whatsapp_marketing, self).write(vals)

    def validation_of_name(self, name):
        res = False
        for name_element in name:
            if name_element.isupper() or name_element.isspace():
                raise UserError(_("The name can only contain lowercase alphanumeric characters and underscores (_). Cannot contain uppercase,space characters"))
        if ('\\n' in name) or ('\\t' in name) or ('\\b' in name):
            raise UserError(_("The name can only contain lowercase alphanumeric characters and underscores (_). Cannot contain uppercase,space characters"))
        return res

    def action_create_whatsapp_template(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Message',
            'res_model': 'marketing.confirmation.template.wizard',
            'view_mode': 'form',
            'view_id': self.env['ir.model.data']._xmlid_to_res_id('pragtech_whatsapp_base.view_marketing_confirmation_template_wizard_form'),
            'target': 'new',
            'nodestroy': True,
        }

    def action_view_whatsapp_template(self):
        ctx = self._context.copy()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Whatsapp Template',
            'res_model': 'whatsapp.templates',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx.update({'whatsapp_marketing_id': self.id}),
            'res_id' : self.whatsapp_template_id.id,
            'nodestroy': True,
        }

    def _whatsapp_compute_next_departure(self):
        cron_next_call = self.env.ref('pragmatic_odoo_whatsapp_marketing.send_whatsapp_msg_marketing').sudo().nextcall
        str2dt = fields.Datetime.from_string
        cron_time = str2dt(cron_next_call)
        for whatsapp_message in self:
            if whatsapp_message.schedule_date:
                schedule_date = str2dt(whatsapp_message.schedule_date)
                whatsapp_message.next_departure = max(schedule_date, cron_time)
            else:
                whatsapp_message.next_departure = cron_time

    @api.depends('whatsapp_model_id')
    def _compute_model(self):
        for record in self:
            record.whatsapp_model_real = record.whatsapp_model_name or 'whatsapp.contact'

    @api.depends('whatsapp_model_name', 'odoo_group_ids')
    def _compute_whatsapp_domain(self):
        for message in self:
            if not message.whatsapp_model_name:
                message.whatsapp_domain = ''
            else:
                message.whatsapp_domain = repr(message._get_default_message_domain())

    def _get_default_message_domain(self):
        message_domain = []
        return message_domain

    def _get_remaining_recipients(self):
        res_ids = self._get_recipients()
        return res_ids

    def _get_recipients(self):
        message_domain = self._parse_message_domain()
        res_ids = self.env[self.whatsapp_model_real].search(message_domain).ids
        return res_ids

    def _parse_message_domain(self):
        self.ensure_one()
        try:
            message_domain = literal_eval(self.whatsapp_domain)
        except Exception:
            message_domain = [('id', 'in', [])]
        return message_domain

    def action_send_message(self):
        if self.whatsapp_instance_id.provider == 'whatsapp_chat_api':
            self.chat_api_send_whatsapp_message()
        elif self.whatsapp_instance_id.provider == 'gupshup':
            self.gupshup_send_whatsapp_message()
        elif self.whatsapp_instance_id.provider == 'meta':
            self.meta_send_whatsapp_message()

    def meta_send_whatsapp_message(self):
        token = self.whatsapp_instance_id.whatsapp_meta_api_token
        number_id = self.whatsapp_instance_id.whatsapp_meta_phone_number_id
        url = "https://graph.facebook.com/v16.0/{}/messages".format(number_id)
        req_headers = CaseInsensitiveDict()
        req_headers["Authorization"] = "Bearer " + token
        req_headers["Content-Type"] = "application/json"
        recepient = self.whatsapp_model_real

        if recepient == 'odoo.group':
            odoo_group_rec = self.env['odoo.group'].sudo().search([])
            for group_rec in odoo_group_rec:
                for partner in group_rec.partner_ids:
                    number = partner.mobile
                    message = self.message_body
                    data_json = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": number,
                        "type": "text",
                        "text": {
                            "body": message,
                        }
                    }
                    response = requests.post(url, headers=req_headers, json=data_json)
                    if response.status_code in [202, 201, 200]:
                        self.state = 'done'
                        _logger.info("\nSend Message successfully")

        if recepient == 'res.partner':
            res_partner_rec = self.env['res.partner'].sudo().search([])
            for partner_rec in res_partner_rec:
                for partner in partner_rec:
                    number = partner.mobile
                    data_json = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": number,
                        "type": "text",
                        "text": {
                            "body": self.message_body,
                        }
                    }
                    response = requests.post(url, headers=req_headers, json=data_json)
                    if response.status_code in [202, 201, 200]:
                        self.state = 'done'
                        _logger.info("\nSend Message successfully")

        if recepient == 'crm.lead':
            crm_lead_rec = self.env['crm.lead'].sudo().search([])
            for lead_rec in crm_lead_rec:
                for partner in lead_rec:
                    number = partner.name
                    data_json = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": number,
                        "type": "text",
                        "text": {
                            "body": self.message_body,
                        }
                    }
                    response = requests.post(url, headers=req_headers, json=data_json)
                    if response.status_code in [202, 201, 200]:
                        self.state = 'done'
                        _logger.info("\nSend Message successfully")

        if recepient == 'sale.order':
            sale_order_rec = self.env['sale.order'].sudo().search([])
            for sale_rec in sale_order_rec:
                for partner in sale_rec.partner_id:
                    number = partner.mobile
                    data_json = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": number,
                        "type": "text",
                        "text": {
                            "body": self.message_body,
                        }
                    }
                    response = requests.post(url, headers=req_headers, json=data_json)
                    if response.status_code in [202, 201, 200]:
                        self.state = 'done'
                        _logger.info("\nSend Message successfully")

        if recepient == 'whatsapp.contact':
            whatsapp_contact_rec = self.env['whatsapp.contact'].sudo().search([])
            for partner in whatsapp_contact_rec:
                number = partner.mobile
                data_json = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": number,
                    "type": "text",
                    "text": {
                        "body": self.message_body,
                    }
                }
                response = requests.post(url, headers=req_headers, json=data_json)
                if response.status_code in [202, 201, 200]:
                    self.state = 'done'
                    _logger.info("\nSend Message successfully")

    def chat_api_send_whatsapp_message(self):
        no_phone_partners = []
        status_url = self.whatsapp_instance_id.whatsapp_endpoint + '/status?token=' + self.whatsapp_instance_id.whatsapp_token
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)
        for record in self:
            res_ids = record._get_remaining_recipients()
            bodies = self.env['mail.render.mixin']._render_template(self.message_body, record.whatsapp_model_real, res_ids, post_process=True)
            for res_id in res_ids:
                rec = self.env[record.whatsapp_model_real].browse(res_id)
                if record.whatsapp_model_real == 'res.partner':
                    if rec.country_id.phone_code and rec.mobile:
                        whatsapp_number = rec.mobile
                        whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                        whatsapp_msg_number_without_code = ''
                        if '+' in whatsapp_msg_number_without_space:
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(rec.country_id.phone_code), "")
                        else:
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(rec.country_id.phone_code), "")
                        number_with_code = str(rec.country_id.phone_code) + whatsapp_msg_number_without_code
                        parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                        message = ''
                        for parameter in parameters:
                            bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                            key = res_id
                            message += bodies[key] + ','
                        sample_message = message[:-1]

                        response = self.chat_api_send_template_message_from_whatsapp_marketing(number_with_code, record, sample_message)
                        if response.status_code == 201 or response.status_code == 200:
                            json_response = json.loads(response.text)
                            if json_response.get('sent') and json_response.get('description') == 'Message has been sent to the provider':
                                _logger.info("\nSend Message successfully")
                                self.state = 'done'
                                bodies = self.env['mail.render.mixin']._render_template(record.message_body, record.whatsapp_model_real, [res_id], post_process=True)
                                whatsapp_messge_body = bodies[res_id]

                                if self.attachment_id:
                                    self.env['whatsapp.msg'].create_whatsapp_message_for_template(number_with_code, whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                          self.whatsapp_instance_id,
                                                                          'whatsapp.marketing', self, self.attachment_id)
                                else:
                                    self.env['whatsapp.msg'].create_whatsapp_message(number_with_code, whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                 "text",
                                                                 self.whatsapp_instance_id, 'whatsapp.marketing', self)
                elif record.whatsapp_model_real == 'sale.order' or record.whatsapp_model_real == 'crm.lead':
                    if rec.partner_id.country_id.phone_code and rec.partner_id.mobile:
                        whatsapp_number = rec.partner_id.mobile
                        whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                        whatsapp_msg_number_without_code = ''
                        if '+' in whatsapp_msg_number_without_space:
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                            '+' + str(rec.partner_id.country_id.phone_code), "")
                        else:
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(rec.partner_id.country_id.phone_code), "")
                        number_with_code = str(rec.partner_id.country_id.phone_code) + whatsapp_msg_number_without_code
                        parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                        message = ''
                        for parameter in parameters:
                            bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                            key = res_id
                            message += bodies[key] + ','
                        sample_message = message[:-1]
                        response = self.chat_api_send_template_message_from_whatsapp_marketing(number_with_code, record, sample_message)
                        if response.status_code == 201 or response.status_code == 200:
                            json_response = json.loads(response.text)
                            if json_response.get('sent') and json_response.get('description') == 'Message has been sent to the provider':
                                _logger.info("\nSend Message successfully")
                                self.state = 'done'
                                bodies = self.env['mail.render.mixin']._render_template(record.message_body, record.whatsapp_model_real, [res_id], post_process=True)
                                whatsapp_messge_body = bodies[res_id]
                                if self.attachment_id:
                                    self.env['whatsapp.msg'].create_whatsapp_message_for_template(number_with_code, whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                                                  self.whatsapp_instance_id,
                                                                                                  'whatsapp.marketing', self, self.attachment_id)
                                else:
                                    self.env['whatsapp.msg'].create_whatsapp_message(number_with_code, whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                                     "text",
                                                                                     self.whatsapp_instance_id, 'whatsapp.marketing', self)

                elif record.whatsapp_model_real == 'odoo.group':
                    for res_partner_id in rec.partner_ids:
                        if rec.whatsapp_contact_ids:
                            for contact_id in rec.whatsapp_contact_ids:
                                if contact_id.sanitized_mobile != res_partner_id.mobile:
                                    whatsapp_number = res_partner_id.mobile
                                    whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                                    whatsapp_msg_number_without_code = ''
                                    if '+' in whatsapp_msg_number_without_space:
                                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                            '+' + str(res_partner_id.country_id.phone_code), "")
                                    else:
                                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(res_partner_id.country_id.phone_code), "")
                                    print("\n========================2=============", whatsapp_msg_number_without_code)
                                    parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                                    message = ''
                                    print("\n=================2=======2=============")
                                    for parameter in parameters:
                                        bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                                        key = res_id
                                        message += bodies[key] + ','
                                    sample_message = message[:-1]
                                    number_with_code = str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code

                                    response = self.chat_api_send_template_message_from_whatsapp_marketing(number_with_code, record, sample_message)
                                    print("\n=================", response.json())
                                    if response.status_code == 201 or response.status_code == 200:
                                        json_response = json.loads(response.text)
                                        if json_response.get('sent') and json_response.get('description') == 'Message has been sent to the provider':
                                            _logger.info("\nSend Message successfully")
                                            self.state = 'done'
                                            bodies = self.env['mail.render.mixin']._render_template(record.message_body, record.whatsapp_model_real, [res_id], post_process=True)
                                            whatsapp_messge_body = bodies[res_id]
                                            if self.attachment_id:
                                                self.env['whatsapp.msg'].create_whatsapp_message_for_template(number_with_code, whatsapp_messge_body, json_response.get('id'),
                                                                                                              json_response.get('message'),
                                                                                                              self.whatsapp_instance_id,
                                                                                                              'whatsapp.marketing', self, self.attachment_id)
                                            else:
                                                self.env['whatsapp.msg'].create_whatsapp_message(number_with_code, whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                                                 "text",
                                                                                                 self.whatsapp_instance_id, 'whatsapp.marketing', self)


                        elif not rec.whatsapp_contact_ids:
                            whatsapp_number = res_partner_id.mobile
                            whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                            whatsapp_msg_number_without_code = ''
                            if '+' in whatsapp_msg_number_without_space:
                                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                    '+' + str(res_partner_id.country_id.phone_code), "")
                            else:
                                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(res_partner_id.country_id.phone_code), "")
                            parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                            message = ''
                            for parameter in parameters:
                                bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                                key = res_id
                                message += bodies[key] + ','
                            sample_message = message[:-1]
                            number_with_code = str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code

                            response = self.chat_api_send_template_message_from_whatsapp_marketing(number_with_code, record, sample_message)

                            if response.status_code == 201 or response.status_code == 200:
                                json_response = json.loads(response.text)
                                if json_response.get('sent') and json_response.get('description') == 'Message has been sent to the provider':
                                    _logger.info("\nSend Message successfully")
                                    self.state = 'done'
                                    bodies = self.env['mail.render.mixin']._render_template(record.message_body, record.whatsapp_model_real, [res_id], post_process=True)
                                    whatsapp_messge_body = bodies[res_id]
                                    if self.attachment_id:
                                        self.env['whatsapp.msg'].create_whatsapp_message_for_template(number_with_code, whatsapp_messge_body, json_response.get('id'),
                                                                                                      json_response.get('message'),
                                                                                                      self.whatsapp_instance_id,
                                                                                                      'whatsapp.marketing', self, self.attachment_id)
                                    else:
                                        self.env['whatsapp.msg'].create_whatsapp_message(number_with_code, whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                                         "text",
                                                                                         self.whatsapp_instance_id, 'whatsapp.marketing', self)

                    for contact_id in rec.whatsapp_contact_ids:
                        parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                        message = ''
                        for parameter in parameters:
                            bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                            key = res_id
                            message += bodies[key] + ','
                        sample_message = message[:-1]
                        response = self.chat_api_send_template_message_from_whatsapp_marketing(str(contact_id.whatsapp_id), record, sample_message)
                        if response.status_code == 201 or response.status_code == 200:
                            json_response = json.loads(response.text)
                            if json_response.get('sent') and json_response.get('description') == 'Message has been sent to the provider':
                                _logger.info("\nSend Message successfully")
                                self.state = 'done'
                                bodies = self.env['mail.render.mixin']._render_template(record.message_body, record.whatsapp_model_real, [res_id], post_process=True)
                                whatsapp_messge_body = bodies[res_id]
                                if self.attachment_id:
                                    self.env['whatsapp.msg'].create_whatsapp_message_for_template(str(contact_id.whatsapp_id), whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                                                  self.whatsapp_instance_id,
                                                                                                  'whatsapp.marketing', self, self.attachment_id)
                                else:
                                    self.env['whatsapp.msg'].create_whatsapp_message(str(contact_id.whatsapp_id), whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                                     "text",
                                                                                     self.whatsapp_instance_id, 'whatsapp.marketing', self)

                elif record.whatsapp_model_real == 'whatsapp.contact':
                    parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                    message = ''
                    for parameter in parameters:
                        bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                        key = res_id
                        message += bodies[key] + ','
                    sample_message = message[:-1]
                    response = self.chat_api_send_template_message_from_whatsapp_marketing(str(rec.mobile), record, sample_message)
                    if response.status_code == 201 or response.status_code == 200:
                        json_response = json.loads(response.text)
                        if json_response.get('sent') and json_response.get('description') == 'Message has been sent to the provider':
                            _logger.info("\nSend Message successfully")
                            self.state = 'done'
                            bodies = self.env['mail.render.mixin']._render_template(record.message_body, record.whatsapp_model_real, [res_id], post_process=True)
                            whatsapp_messge_body = bodies[res_id]
                            if self.attachment_id:
                                self.env['whatsapp.msg'].create_whatsapp_message_for_template(str(rec.mobile), whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                                              self.whatsapp_instance_id,
                                                                                              'whatsapp.marketing', self, self.attachment_id)
                            else:
                                self.env['whatsapp.msg'].create_whatsapp_message(str(rec.mobile), whatsapp_messge_body, json_response.get('id'), json_response.get('message'),
                                                                                 "text",
                                                                                 self.whatsapp_instance_id, 'whatsapp.marketing', self)

    def chat_api_send_template_message_from_whatsapp_marketing(self, number_with_code, record, message):
        if self.whatsapp_template_id and self.whatsapp_template_id.approval_state == 'approved':
            payload = {}
            sample_message = ''
            if ' ' in message:
                sample_message = (message).replace(' ', '')
            else:
                sample_message = message
            split_message = sample_message.split(',')
            parameter_list = []
            for message in split_message:
                parameter_dict = {}
                parameter_dict['type'] = 'text'
                parameter_dict['text'] = message
                parameter_list.append(parameter_dict)
            if self.attachment_id:
                media_id = self.env['whatsapp.msg'].get_media_id(self.attachment_id, self.whatsapp_instance_id)
                payload = {
                    "template": self.whatsapp_template_id.name,
                    "language": {"policy": "deterministic", "code": self.whatsapp_template_id.languages.iso_code},
                    "namespace": self.whatsapp_template_id.namespace,
                    "params": [
                        {
                            "type": "header",
                            "parameters": [{
                            }]
                        },
                        {
                            "type": "body",
                            "parameters": parameter_list
                        }
                    ],
                    "phone": number_with_code
                }
                if 'pdf' in self.attachment_id.mimetype or 'text' in self.attachment_id.mimetype:
                    payload.get('params')[0].get('parameters')[0].update({'type': 'document'})
                    payload.get('params')[0].get('parameters')[0].update({'document': {"id": media_id, "filename": self.attachment_id.name}})
                elif 'image' in self.attachment_id.mimetype:
                    payload.get('params')[0].get('parameters')[0].update({'image': {"id": media_id, "filename": self.attachment_id.name}})
                    payload.get('params')[0].get('parameters')[0].update({'type': 'image'})
                elif 'video' in self.attachment_id.mimetype:
                    payload.get('params')[0].get('parameters')[0].update({'video': {"id": media_id, "filename": self.attachment_id.name}})
                    payload.get('params')[0].get('parameters')[0].update({'type': 'video'})
            else:
                payload = {
                    "template": self.whatsapp_template_id.name,
                    "language": {"policy": "deterministic", "code": self.whatsapp_template_id.languages.iso_code},
                    "namespace": self.whatsapp_template_id.namespace,
                    "params": [
                        {
                            "type": "body",
                            "parameters": parameter_list
                        }
                    ],
                    "phone": number_with_code
                }
            url = self.whatsapp_instance_id.whatsapp_endpoint + '/sendTemplate?token=' + self.whatsapp_instance_id.whatsapp_token
            headers = {"Content-Type": "application/json"}
            return requests.post(url, data=json.dumps(payload), headers=headers)

        elif not self.whatsapp_template_id or not self.whatsapp_template_id.approval_state:
            self.env['whatsapp.msg'].template_errors(self.whatsapp_template_id)

    def gupshup_send_whatsapp_message(self):
        for record in self:
            res_ids = record._get_remaining_recipients()
            bodies = self.env['mail.render.mixin']._render_template(self.message_body, record.whatsapp_model_real, res_ids, post_process=True)
            for res_id in res_ids:
                rec = self.env[record.whatsapp_model_real].browse(res_id)
                if record.whatsapp_model_real == 'res.partner':
                    if rec.country_id.phone_code and rec.mobile:
                        whatsapp_number = rec.mobile
                        whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                        whatsapp_msg_number_without_code = ''
                        if '+' in whatsapp_msg_number_without_space:
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace('+' + str(rec.country_id.phone_code), "")
                        else:
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(rec.country_id.phone_code), "")
                        number_with_code = str(rec.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                        message = ''
                        for parameter in parameters:
                            bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                            key = res_id
                            message += bodies[key] + ','
                        sample_message = message[:-1]
                        record.with_context({'partner_id': rec.id}).gupshup_send_create_whatsapp_message_through_template(res_id, bodies, rec, number_with_code, sample_message)
                elif record.whatsapp_model_real == 'sale.order' or record.whatsapp_model_real == 'crm.lead':
                    if rec.partner_id.country_id.phone_code and rec.partner_id.mobile:
                        whatsapp_number = rec.partner_id.mobile
                        whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                        whatsapp_msg_number_without_code = ''
                        if '+' in whatsapp_msg_number_without_space:
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                '+' + str(rec.partner_id.country_id.phone_code), "")
                        else:
                            whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(rec.partner_id.country_id.phone_code), "")
                        parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                        message = ''
                        for parameter in parameters:
                            bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                            key = res_id
                            message += bodies[key] + ','
                        sample_message = message[:-1]
                        number_with_code = str(rec.partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                        record.with_context({'partner_id': rec.partner_id.id}).gupshup_send_create_whatsapp_message_through_template(res_id, bodies, rec, number_with_code, sample_message)

                elif record.whatsapp_model_real == 'odoo.group':
                    for res_partner_id in rec.partner_ids:
                        if rec.whatsapp_contact_ids:
                            for contact_id in rec.whatsapp_contact_ids:
                                if contact_id.sanitized_mobile != res_partner_id.mobile:
                                    whatsapp_number = res_partner_id.mobile
                                    whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                                    whatsapp_msg_number_without_code = ''
                                    if '+' in whatsapp_msg_number_without_space:
                                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                            '+' + str(res_partner_id.country_id.phone_code), "")
                                    else:
                                        whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(res_partner_id.country_id.phone_code), "")
                                    number_with_code = str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                                    parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                                    message = ''
                                    for parameter in parameters:
                                        bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                                        key = res_id
                                        message += bodies[key] + ','
                                    sample_message = message[:-1]
                                    record.with_context({'partner_id': res_partner_id.id}).gupshup_send_create_whatsapp_message_through_template(res_id, bodies, rec, number_with_code, sample_message)

                        elif not rec.whatsapp_contact_ids:
                            whatsapp_number = res_partner_id.mobile
                            whatsapp_msg_number_without_space = whatsapp_number.replace(" ", "")
                            whatsapp_msg_number_without_code = ''
                            if '+' in whatsapp_msg_number_without_space:
                                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(
                                    '+' + str(res_partner_id.country_id.phone_code), "")
                            else:
                                whatsapp_msg_number_without_code = whatsapp_msg_number_without_space.replace(str(res_partner_id.country_id.phone_code), "")
                            number_with_code = str(res_partner_id.country_id.phone_code) + "" + whatsapp_msg_number_without_code
                            parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                            message = ''
                            for parameter in parameters:
                                bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                                key = res_id
                                message += bodies[key] + ','
                            sample_message = message[:-1]
                            record.with_context({'partner_id': res_partner_id.id}).gupshup_send_create_whatsapp_message_through_template(res_id, bodies, rec, number_with_code, sample_message)
                    for contact_id in rec.whatsapp_contact_ids:
                        record.with_context({'partner_id': contact_id.partner_id.id, 'whatsapp_contact_from_odoo_group': True}).gupshup_send_create_whatsapp_message(res_id, bodies, rec, str(contact_id.whatsapp_id))

                elif record.whatsapp_model_real == 'whatsapp.contact':
                    parameters = ['{{ ' + value + ' }}' for value in (record.message_body).split() if value.startswith('object.')]
                    message = ''
                    for parameter in parameters:
                        bodies = self.env['mail.render.mixin']._render_template(parameter, record.whatsapp_model_real, [res_id], post_process=True)
                        key = res_id
                        message += bodies[key] + ','
                    sample_message = message[:-1]
                    record.with_context({'partner_id': rec.partner_id.id}).gupshup_send_create_whatsapp_message_through_template(res_id, bodies, rec, str(rec.whatsapp_id), sample_message)

    def gupshup_send_create_whatsapp_message(self, res_id, bodies, rec, number_with_code):
        url = 'https://api.gupshup.io/sm/api/v1/msg'
        headers = {"Content-Type": "application/x-www-form-urlencoded", "apikey": self.whatsapp_instance_id.whatsapp_gupshup_api_key}
        for key, value in bodies.items():
            if res_id == key:
                payload = {
                    'channel': 'whatsapp',
                    'source': self.whatsapp_instance_id.gupshup_source_number,
                    'destination': number_with_code,
                    'message': json.dumps({
                        'type': 'text',
                        'text': str(value)
                    })
                }
                response = requests.post(url, headers=headers, data=payload)
                if response.status_code == 201 or response.status_code == 200 or response.status_code == 202:
                    json_send_message_response = json.loads(response.text)
                    self.write({'state': 'done'})
                    self.env['whatsapp.msg.marketing'].gupshup_marketing_create_whatsapp_message(number_with_code, str(value), json_send_message_response.get('messageId'), self.whatsapp_instance_id,
                                                                                                                   'whatsapp.marketing', self)

        if self.attachment_id:
            attachment_data = {
                'channel': 'whatsapp',
                'source': self.whatsapp_instance_id.gupshup_source_number,
                'destination': number_with_code,
            }
            attachment_data = self.env['whatsapp.msg.res.partner'].gupshup_create_attachment_dict_for_send_message(self.attachment_id, attachment_data)
            response = requests.post(url, data=attachment_data, headers=headers)
            if response.status_code in [202, 201, 200]:
                _logger.info("\nSend Attachment successfully from gupshup")
                response_dict = response.json()
                self.env['whatsapp.msg.marketing'].gupshup_marketing_create_whatsapp_message_for_attachment(number_with_code, self.attachment_id, json_send_message_response.get('messageId'),
                                                                                             self.attachment_id.mimetype,self.whatsapp_instance_id,
                                                                                             'whatsapp.marketing', self)


    def gupshup_send_create_whatsapp_message_through_template(self, res_id, bodies, rec, number_with_code, message):
        whatsapp_template_id = self.env['whatsapp.templates'].sudo().search([('name', '=', self.name), ('whatsapp_instance_id', '=', self.whatsapp_instance_id.id)], limit=1)
        if whatsapp_template_id and whatsapp_template_id.approval_state == 'APPROVED':
            sample_message = ''
            if ' ' in message:
                sample_message = (message).replace(' ', '')
            else:
                sample_message = message
            split_message = sample_message.split(',')
            parameter_list = []
            for message in split_message:
                parameter_list.append(message)
            payload = {
                "source": self.whatsapp_instance_id.gupshup_source_number,
                "destination": number_with_code,
                "template": json.dumps({"id": whatsapp_template_id.template_id, "params": parameter_list}),
            }
            if self.attachment_id:
                if 'image' in self.attachment_id.mimetype:
                    payload['message'] = json.dumps({"type": "image", "image": {"link": self.attachment_id.public_url, "filename": self.attachment_id.name}})
                elif 'application/pdf' in self.attachment_id.mimetype or 'text' in self.attachment_id.mimetype:
                    payload['message'] = json.dumps({"type": "document", "document": {"link": self.attachment_id.public_url, "filename": self.attachment_id.name}})
                elif 'video' in self.attachment_id.mimetype:
                    payload['message'] = json.dumps({"type": "video", "video": {"link": self.attachment_id.public_url, "filename": self.attachment_id.name}})

            url = 'https://api.gupshup.io/sm/api/v1/template/msg'
            headers = {"Content-Type": "application/x-www-form-urlencoded", "apikey": self.whatsapp_instance_id.whatsapp_gupshup_api_key}
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 201 or response.status_code == 200 or response.status_code == 202:
                json_response = json.loads(response.text)
                self.state = 'done'
                bodies = self.env['mail.render.mixin']._render_template(self.message_body, self.whatsapp_model_real, [res_id], post_process=True)
                whatsapp_messge_body = bodies[res_id]
                if self.attachment_id:
                    self.env['whatsapp.msg.res.partner'].gupshup_create_whatsapp_message(
                        number_with_code, whatsapp_messge_body, json_response.get('messageId'), self.whatsapp_instance_id, 'whatsapp.marketing',
                        self, self.attachment_id)
                else:
                    self.env['whatsapp.msg.res.partner'].gupshup_create_whatsapp_message(
                        number_with_code, whatsapp_messge_body, json_response.get('messageId'), self.whatsapp_instance_id, 'whatsapp.marketing',
                        self)


        elif not whatsapp_template_id or not whatsapp_template_id.approval_state or whatsapp_template_id.approval_state == 'REJECTED':
            self.env['whatsapp.msg'].template_errors(whatsapp_template_id)

    def action_schedule(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("pragmatic_odoo_whatsapp_marketing.whatsapp_message_schedule_date_action")
        action['context'] = dict(self.env.context, default_odoo_group_id=self.id)
        return action

    def action_cancel(self):
        self.write({'state': 'draft', 'schedule_date': False})

    def _send_schedule_messages(self):
        mass_messages = self.search(
            [('state', '=', ('in_queue')), '|', ('schedule_date', '<', fields.Datetime.now()),
            ('schedule_date', '=', False)])
        for mass_message in mass_messages:
            user = mass_message.write_uid or self.env.user
            mass_message = mass_message.with_context(**user.with_user(user).context_get())
            if len(mass_message._get_remaining_recipients()) > 0:
                mass_message.action_send_message()
            else:
                mass_message.write({'state': 'done', 'sent_date': fields.Datetime.now()})

        messages = self.env['whatsapp.marketing'].search([
            ('state', '=', 'done'),
            ('sent_date', '<=', fields.Datetime.now() - relativedelta(days=1)),
            ('sent_date', '>=', fields.Datetime.now() - relativedelta(days=5)),
        ])
        # if messages:
        #     messages.action_send_message()

    def action_reset_to_draft(self):
        whatsapp_marketing_dict = {}
        if self.schedule_date:
            whatsapp_marketing_dict['schedule_date'] = False
        whatsapp_marketing_dict['state'] = 'draft'
        self.write(whatsapp_marketing_dict)

    @api.onchange('model_object_field', 'sub_model_object_field', 'null_value')
    def _onchange_dynamic_placeholder(self):
        """ Generate the dynamic placeholder """
        if self.model_object_field:
            if self.model_object_field.ttype in ['many2one', 'one2many', 'many2many']:
                model = self.env['ir.model']._get(self.model_object_field.relation)
                if model:
                    self.sub_object = model.id
                    sub_field_name = self.sub_model_object_field.name
                    self.copyvalue = self._build_expression(self.model_object_field.name,
                                                            sub_field_name, self.null_value or False)
            else:
                self.sub_object = False
                self.sub_model_object_field = False
                self.copyvalue = self._build_expression(self.model_object_field.name, False, self.null_value or False)
        else:
            self.sub_object = False
            self.copyvalue = False
            self.sub_model_object_field = False
            self.null_value = False

    @api.model
    def _build_expression(self, field_name, sub_field_name, null_value):
        """Returns a placeholder expression for use in a template field,
        based on the values provided in the placeholder assistant.

        :param field_name: main field name
        :param sub_field_name: sub field name (M2O)
        :param null_value: default value if the target value is empty
        :return: final placeholder expression """
        expression = ''
        if field_name:
            expression = "{{ object." + field_name
            if sub_field_name:
                expression += "." + sub_field_name
            if null_value:
                expression += " or '''%s'''" % null_value
            expression += " }}"
        return expression



    @api.onchange('whatsapp_templates_id')
    def whatsapp_template(self):
        if self:
            self.message_body=self.whatsapp_templates_id.body
        