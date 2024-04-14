from odoo import fields, models

class HubspotActivity(models.Model):
    
    _name = "hubspot.custom.field"

    hubspot_name = fields.Char('Hubspot Field Name')
    odoo_name = fields.Char('Odoo Field Name')
    object_type = fields.Selection([('product','Product'),('partner','Partner'),('company','Company'),('lead','Lead')],string="Object Type")


    connection_id = fields.Many2one(comodel_name='channel.connection')
