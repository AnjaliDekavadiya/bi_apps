from odoo import models, fields, api

class WhatsAppContact(models.Model):
    _name = 'whatsapp.contact'

    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    