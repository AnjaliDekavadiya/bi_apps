from odoo import models

class TypeOperationSunat(models.Model):
    _name = 'type.operation.sunat'
    _description = 'Type Operation Sunat'
    _inherit = 'sunat.catalog.tmpl'
