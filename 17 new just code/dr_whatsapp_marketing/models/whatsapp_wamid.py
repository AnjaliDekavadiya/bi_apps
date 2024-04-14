from odoo import models, fields, api
import logging
class WhatsAppWAMID(models.Model):
    _name = 'whatsapp.wamid'

    wamid = fields.Char(string='WAMID')
    response = fields.Char(string='Response')
    is_read = fields.Integer(string='Read')
    is_sent = fields.Integer(string='Sent')
    is_delivered = fields.Integer(string='Delivered')
    is_replied = fields.Integer(string='Replied')
    is_bounced = fields.Integer(string='Bounced')
    template_id = fields.Char(string='Template ID')
    contact = fields.Char(string='Contact')
    campaign = fields.Char(string='Campaign')
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent')
    ], 'Status')
    scheduled_date = fields.Datetime(string='Scheduled Date')
    header = fields.Text(string='Header')
    body = fields.Text(string='Body')
    buttons = fields.One2many('whatsapp.button', 'wamid', string='Buttons')
    
    @api.model
    def schedule_message(self):
        logging.info("SCHEDULED MESSAGE")
        
        scheduled_messages = self.search([("state", "=", "scheduled"), ("scheduled_date", "<=", fields.datetime.now())])
        
        for message in scheduled_messages:
            if("campaign" in message):
                campaign = self.env['whatsapp.message'].search([("id", "=", message["campaign"])], limit=1)
                if(campaign):
                    campaign.sudo().write({ "state": "sent" })
            self.env['whatsapp.message'].send_message([message.contact], message.template_id, message.body, message.buttons, message.header, message.campaign, True, message.id)