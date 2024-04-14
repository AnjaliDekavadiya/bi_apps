# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from datetime import datetime, timedelta, date


class MaintenanceChecklist(models.Model):
    _name = "maintenance.checklist"
    _description = 'Maintenance Checklist'

    name = fields.Char("Checklist Name")
    description = fields.Text("Description")
    is_validated = fields.Boolean('Is validated?')
    maintenance_req_id = fields.Many2one('maintenance.request', "Maintenance Request")


class Porducts(models.Model):
    _name = "products"
    _description = 'Products'

    maintenance_equip_id = fields.Many2one('maintenance.equipment', "Maintenance Equipment")
    maintenance_req_id = fields.Many2one('maintenance.request', "Maintenance Request")
    product_id = fields.Many2one('product.template', 'Product')
    name = fields.Char("Description", related="product_id.name")
    qty = fields.Float('Quantity', default=1)
    uom_id = fields.Many2one('uom.uom', "UOM", related="product_id.uom_id", store=True)
