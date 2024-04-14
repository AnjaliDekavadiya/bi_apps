# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from datetime import datetime, timedelta, date


class EquiomentInherit(models.Model):
    _inherit = 'maintenance.equipment'

    equi_checklist_ids = fields.Many2many('maintenance.checklist')
    products_ids = fields.One2many('products', 'maintenance_equip_id', "Products")
