# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PropertyDocument(models.Model):
    _name = 'property.document'
    _description = "Property Document"

    name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    file = fields.Binary(required=True)
    property_id = fields.Many2one('product.product', "Source Document")

class PropertyImages(models.Model):
    _name = 'property.image'
    _description = "Property Image"

    name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    file = fields.Binary(required=True)
    property_id = fields.Many2one('product.product', "Source Document")
