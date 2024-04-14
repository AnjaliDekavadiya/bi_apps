# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import api, fields, models
from odoo.exceptions import AccessDenied

class ResUsers(models.Model):
    _inherit = 'res.users'

    otp_access_token = fields.Char(string="Access token for Otp")

    def _check_credentials(self, password, env):
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            if self.env.user.active:
                otp_obj = self.env['otp.otp'].sudo().search([('is_used','=',False),('user_email','=',self.login)], limit=1, order="id desc")
                res = self.sudo().search([('id', '=', self.env.uid)])
                if res and otp_obj and otp_obj.otp_name == password:
                    return
            raise