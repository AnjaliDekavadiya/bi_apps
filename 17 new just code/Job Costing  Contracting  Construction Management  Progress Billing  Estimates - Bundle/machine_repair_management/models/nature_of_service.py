# -*- coding: utf-8 -*

from odoo import models, fields, api

class ServiceNature(models.Model):
    _name = 'service.nature'
    _description = "Service Nature"
    
    name = fields.Char(
       string="Name",
       required=True,
    )
