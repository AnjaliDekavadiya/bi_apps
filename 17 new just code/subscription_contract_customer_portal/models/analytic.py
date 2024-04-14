# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models, tools, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def _default_access_token(self):
        return uuid.uuid4().hex

    access_token = fields.Char('Access Token', default=_default_access_token)