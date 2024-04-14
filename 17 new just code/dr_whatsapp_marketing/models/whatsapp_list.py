from odoo import models, fields, api

class WhatsAppContact(models.Model):
    _name = 'whatsapp.list'

    name = fields.Char(string='Name', required=True)
    contacts = fields.Many2many('whatsapp.contact', string='Contacts')
    