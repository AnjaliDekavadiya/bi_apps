# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class TenderVendors(models.Model):
    _inherit = 'res.partner'

    is_vendor = fields.Boolean()
    tender_category_ids = fields.Many2many('tender.type', string="Tender Category")
