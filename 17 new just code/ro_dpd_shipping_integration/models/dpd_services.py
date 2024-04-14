from odoo import models, fields, api


class DPDServices(models.Model):
    _name = 'dpd.services'

    service_id = fields.Char(string='Service Id', help="Id Of Services Which is given by dpd")
    name = fields.Char(string='Service Name', help="Type Of Service Name")