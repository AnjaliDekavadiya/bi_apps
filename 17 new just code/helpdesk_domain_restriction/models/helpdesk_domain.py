from odoo import api, fields, models, _

class HelpdeskDomain(models.Model):
    _name = 'helpdesk.domain'

    name = fields.Char(string='Domain Name', required=True)

    