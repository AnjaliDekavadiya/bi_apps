from odoo import models, fields, api
from heyoo import WhatsApp
from odoo.exceptions import UserError, ValidationError
import logging
class WhatsAppMessage(models.Model):
    _name = 'whatsapp.message'

    name = fields.Char(string='Name', required=True)
    recipient_type = fields.Selection([
        ('contact', 'Contact'),
        ('list', 'List')
    ], 'Recipient', default='list', required=True)
    contact_ids = fields.Many2many('whatsapp.contact', string='Contacts')
    list_ids = fields.Many2many('whatsapp.list', string='Lists')
    template_id = fields.Many2one('whatsapp.template', string='Template', required=True)
    header = fields.Text(string='Header')
    body = fields.Text(string='Body')
    buttons = fields.One2many('whatsapp.button', 'message', string='Buttons')
    scheduled_date = fields.Datetime(string='Scheduled Date')
    sending_date = fields.Datetime(string='Sending Date')
    
    received_ratio = fields.Integer(compute="_compute_statistics", string='Delivered')
    opened_ratio = fields.Integer(compute="_compute_statistics", string='Opened')
    replied_ratio = fields.Integer(compute="_compute_statistics", string='Replied')
    bounced_ratio = fields.Integer(compute="_compute_statistics", string='Bounced')
    sent = fields.Integer(compute="_compute_statistics", string='Sent')
    scheduled = fields.Integer(compute="_compute_statistics", string='Scheduled')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('error', 'Error'),
        ('sent', 'Sent')
    ], 'State', default='draft')

    @api.model
    def send_message(self, contacts, template, body, buttons = [], header = "", campaign = "", scheduled = False, wamid_odoo_id = 0):
        if(contacts):
                if(scheduled):
                    template = self.env['whatsapp.template'].search([('template_id', '=', template)], limit=1)
                else:
                    template = self.env['whatsapp.template'].search([('id', '=', template)], limit=1)
                
                if(not(template)):
                    raise UserError('Template not found.')
                
                if(template.status == "PENDING"):
                    raise UserError('Cannot use a template with a status of PENDING.')
                
                token = self.env['ir.config_parameter'].sudo().get_param('whatsapp.access_token')
                phone_number_id = self.env['ir.config_parameter'].sudo().get_param('whatsapp.phone_id')
                whatsapp = WhatsApp(token,  phone_number_id=phone_number_id)
                
                if(not(header)):
                    header = []
                else:
                    header = list(map(lambda x: { "type": "text", "text": x }, header.split(",")))
                
                if(not(body)):
                    body = []
                else:
                    body = list(map(lambda x: { "type": "text", "text": x }, body.split(",")))
                
                if(buttons):
                    logging.info("BUTTONS")
                    logging.info(buttons)
                    buttonsData = []
                    for button in buttons:
                        buttonObj = { "type": "button", "sub_type": button.payload_type_send, "index": int(button.index) - 1, "parameters": [] }
                        if(button.payload_type_send == "quick_reply"):
                            buttonObj["parameters"].append({ "type": "payload", "payload": button.payload })
                        else:
                            buttonObj["parameters"].append({ "type": "text", "text": button.payload })
                            
                        buttonsData.append(buttonObj)
                    buttons = buttonsData
                
                wamids = []
                for contact in contacts:
                    if(contact):
                        try:
                            response = whatsapp.send_template(template.name, contact, components=[
                                {
                                    "type": "header",
                                    "parameters": header
                                },
                                {
                                    "type": "body",
                                    "parameters": body
                                },
                                *buttons
                            ], lang=template.language)
                            
                            if("error" in response):
                                if(scheduled):
                                    wamid_res = self.env['whatsapp.wamid'].search([('id', '=', wamid_odoo_id)], limit=1)
                                    wamid_res.sudo().write({ "is_bounced": 1 })
                                else:
                                    self.env['whatsapp.wamid'].sudo().create({ "contact": contact, "template_id": template.template_id, "campaign": campaign, "is_bounced": 1 })
                                continue
                            
                            if("messages" in response and "contacts" in response):
                                wamid = response["messages"][0]["id"]
                                wamids.append(wamid)
                                
                                contact = response["contacts"][0]["input"].replace(" ", "")
                                
                                if(scheduled):
                                    wamid_res = self.env['whatsapp.wamid'].search([('id', '=', wamid_odoo_id)], limit=1)
                                    wamid_res.sudo().write({ "wamid": wamid, "is_sent": 1, "state": "sent" })
                                else:
                                    self.env['whatsapp.wamid'].sudo().create({ "wamid": wamid, "contact": contact, "template_id": template.template_id, "campaign": campaign, "is_sent": 1, "state": "sent" })
                            
                            logging.info(response)        
                        except:
                            if(scheduled):
                                wamid_res = self.env['whatsapp.wamid'].search([('id', '=', wamid_odoo_id)], limit=1)
                                wamid_res.sudo().write({ "is_bounced": 1 })
                            else:
                                self.env['whatsapp.wamid'].sudo().create({ "contact": contact, "template_id": template.template_id, "campaign": campaign, "is_bounced": 1 })
                        
                return wamids
    
    def send_message_action(self):
        for record in self:
            recipient_type, contacts, list_ids, template_id, header, body, buttons, scheduled_date = record.recipient_type, record.contact_ids, record.list_ids, record.template_id, record.header, record.body, record.buttons, record.scheduled_date
            
            if(recipient_type == "contact"):
                if(scheduled_date):
                    record.write({ "state": "scheduled", "sending_date": scheduled_date })
                    if(buttons):
                        buttons_data = []
                        count = 0
                        for button in buttons:
                            buttons_data.append([0, count, { "payload": button.payload, "payload_type_send": button.payload_type_send, "index": button.index }])
                            count += 1
                        buttons = buttons_data
                    
                    for contact in contacts:
                        self.env['whatsapp.wamid'].sudo().create({ "contact": contact.phone, "template_id": template_id.template_id, "header": header, "body": body, "buttons": buttons, "scheduled_date": scheduled_date, "state": "scheduled", "campaign": record.id })
                else:
                    record.write({ "state": "sent", "sending_date": fields.datetime.now() })
                    contact_ids = []
                    for contact in contacts:
                        contact_ids.append(contact.phone)
                    
                    self.send_message(contact_ids, template_id.id, body, buttons, header, campaign=record.id)
            elif(recipient_type == "list"):
                if(scheduled_date):
                    record.write({ "state": "scheduled", "sending_date": scheduled_date })
                    if(buttons):
                        buttons_data = []
                        count = 0
                        for button in buttons:
                            logging.info(button)
                            buttons_data.append([0, count, { "payload": button.payload, "payload_type_send": button.payload_type_send, "index": button.index }])
                            count += 1
                        buttons = buttons_data
                        
                    for list_id in list_ids:
                        for contact in list_id.contacts:
                            self.env['whatsapp.wamid'].sudo().create({ "contact": contact.phone, "template_id": template_id.template_id, "header": header, "body": body, "buttons": buttons, "scheduled_date": scheduled_date, "state": "scheduled", "campaign": record.id })
                else:
                    record.write({ "state": "sent", "sending_date": fields.datetime.now() })
                    contact_ids = []
                    for list_id in list_ids:
                        for contact in list_id.contacts:
                            contact_ids.append(contact.phone)
                    
                    self.send_message(contact_ids, template_id.id, body, buttons, header, campaign=record.id)
            else:
                raise ValidationError('Invalid recipient')
                
            
    def send_message_list_action(self):
        for record in self:
            list_ids, template_id, header, body, buttons, scheduled_date = record.list_ids, record.template_id, record.header, record.body, record.buttons, record.scheduled_date
            
            if(scheduled_date):
                if(buttons):
                    buttons_data = []
                    count = 0
                    for button in buttons:
                        logging.info(button)
                        buttons_data.append([0, count, { "payload": button.payload, "payload_type_send": button.payload_type_send, "index": button.index }])
                        count += 1
                    buttons = buttons_data
                    
                for list_id in list_ids:
                    for contact in list_id.contacts:
                        self.env['whatsapp.wamid'].sudo().create({ "contact": contact.phone, "template_id": template_id.template_id, "header": header, "body": body, "buttons": buttons, "scheduled_date": scheduled_date, "state": "scheduled", "campaign": record.id })
            else:
                logging.info(list_id.contacts)
                contact_ids = []
                for list_id in list_ids:
                    for contact in list_id.contacts:
                        contact_ids.append(contact.phone)
                
                self.send_message(contact_ids, template_id.id, body, buttons, header, campaign=record.id)

    def _compute_statistics(self):
        for record in self:
            delivered = len(self.env["whatsapp.wamid"].sudo().search([("campaign", "=", record.id), ("is_delivered", "=", 1)]))
            opened = len(self.env["whatsapp.wamid"].sudo().search([("campaign", "=", record.id), ("is_read", "=", 1)]))
            replied = len(self.env["whatsapp.wamid"].sudo().search([("campaign", "=", record.id), ("is_replied", "=", 1)]))
            bounced = len(self.env["whatsapp.wamid"].sudo().search([("campaign", "=", record.id), ("is_bounced", "=", 1)]))
            sent = len(self.env["whatsapp.wamid"].sudo().search([("campaign", "=", record.id), ("is_sent", "=", 1)]))
            scheduled = len(self.env["whatsapp.wamid"].sudo().search([("campaign", "=", record.id), ("state", "=", "scheduled")]))
            total = len(self.env["whatsapp.wamid"].sudo().search([("campaign", "=", record.id)])) or 1
            
            # sent -= bounced
            # opened += received
            # replied += opened
            
            row = {}
            row['received_ratio'] = 100.0 * delivered / total
            row['opened_ratio'] = 100.0 * opened / total
            row['replied_ratio'] = 100.0 * replied / total
            row['bounced_ratio'] = 100.0 * bounced / total
            row['sent'] = sent
            row['scheduled'] = scheduled
            
            if(bounced == total):
                row['state'] = 'error'
            
            record.write(row)
            
    def schedule_message_action(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("dr_whatsapp_marketing.whatsapp_schedule_date_action")
        action['context'] = dict(self.env.context, default_message_id=self.id, dialog_size='medium')
        return action
        
    def cancel_message_action(self):
        for record in self:
            record.write({ "state": "draft" })      
            wamid_res = self.env['whatsapp.wamid'].search([('campaign', '=', record.id)])
            for wamid in wamid_res:
                wamid.sudo().unlink()
                
    def action_view_opened(self):
        return self._action_view_documents_filtered('read')

    def action_view_replied(self):
        return self._action_view_documents_filtered('replied')

    def action_view_bounced(self):
        return self._action_view_documents_filtered('bounced')

    def action_view_delivered(self):
        return self._action_view_documents_filtered('delivered')

    def _action_view_documents_filtered(self, view_filter):
        found_traces = self.env["whatsapp.wamid"].sudo().search([("campaign", "=", self.id), ("is_" + view_filter, "=", 1)])
            
        res_ids = []
        for trace in found_traces:
            contact = self.env["whatsapp.contact"].sudo().search([("phone", "=", trace["contact"])], limit=1)
            if(contact):
                res_ids.append(contact["id"])
        
        logging.info(res_ids)
        
        action = {
            'name': view_filter.capitalize(),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': "whatsapp.contact",
            'domain': [('id', 'in', res_ids)],
            'context': dict(self._context, create=False),
        }
        
        return action
    
    def test(self, message):
        logging.info("From WhatsApp message model: " + str(message))
        return "From WhatsApp message model: " + str(message)
            
        