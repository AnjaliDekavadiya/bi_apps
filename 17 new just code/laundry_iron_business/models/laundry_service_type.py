# -*- coding: utf-8 -*

from odoo import models, fields

class LaundryServiceTypeCustom(models.Model):
    _name = 'laundry.service.type.custom'
    _description = "Laundry Service Type"
    
    name = fields.Char(
       string="Name",
       required=True,
    )
