from odoo import models

class ExistenceTypeSunat(models.Model):
    _name = "existence.type.sunat"
    _description = 'Existence Type Sunat'
    _inherit = 'sunat.catalog.tmpl'

