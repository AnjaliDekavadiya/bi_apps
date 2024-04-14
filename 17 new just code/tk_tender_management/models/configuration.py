# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, api, fields


class TenderType(models.Model):
    _name = 'tender.type'
    _description = "Tender Type"

    name = fields.Char(string="Type",translate=True)
    is_site_specific = fields.Boolean(string="Site-Specific Tender")


class DocumentType(models.Model):
    _name = 'document.type'
    _description = "Document Type"

    name = fields.Char(string="Title",translate=True)
    type = fields.Selection([('tender', 'Tender Document'), ('bid', 'Bid Document')])

