# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    not_allow_partial_payment = fields.Boolean("Not Allow Partial Payment")
