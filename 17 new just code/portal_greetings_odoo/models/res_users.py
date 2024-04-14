# -*- coding: utf-8 -*-

import pytz
from datetime import datetime
from odoo import models, fields, api


class Users(models.Model):
    _inherit = 'res.users'

    def _get_hours_today_custom(self):
        now = fields.Datetime.now()
        now_utc = pytz.utc.localize(now)
        tz = pytz.timezone(self.tz)
        now_tz = now_utc.astimezone(tz)        
        return str(now_tz.time())