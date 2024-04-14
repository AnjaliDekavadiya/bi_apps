from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
import logging


class WhatsAppButton(models.TransientModel):
    _name = 'whatsapp.button'

    text = fields.Char(string='Text')
    payload = fields.Char(string='Payload', default='')
    payload_type = fields.Selection([
        ('QUICK_REPLY', 'Quick Reply'),
        ('PHONE', 'Phone'),
        ('URL', 'URL')], string='Type', default='QUICK_REPLY')
    payload_type_send = fields.Selection([
        ('quick_reply', 'Quick Reply'),
        ('text', 'URL')], string='Type', default='quick_reply')
    example = fields.Char(string='Example', default='')
    description = fields.Char(string='Description', default='')
    index = fields.Char(string='Index', default='1')
    template = fields.Char(string='Template')
    message = fields.Char(string='Message')
    wamid = fields.Char(string='WAMID')
    action = fields.Char(string='Action')
    