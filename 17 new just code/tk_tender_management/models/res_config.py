# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class Website(models.Model):
    _inherit = "website"

    followup_user_ids = fields.Many2many('res.users', string="Followup Responsible")
    auto_create = fields.Boolean()


class TenderConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    followup_user_ids = fields.Many2many('res.users', string="Followup Responsible",
                                         related="website_id.followup_user_ids", readonly=False)
    auto_create = fields.Boolean(related="website_id.auto_create", string="Auto Create Vendor Portal User",
                                 readonly=False)
