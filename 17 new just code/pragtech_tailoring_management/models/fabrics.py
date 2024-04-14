from odoo import fields,models,api


class TailoringFabric (models.Model):
    _name = "tailoring.fabric"
    _description = "tailoring_fabric"

    name = fields.Char('Name of Fabric')

    
