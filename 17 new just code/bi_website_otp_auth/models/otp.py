# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import api, fields, models

class Otp(models.Model):
    _name = 'otp.otp'
    _description = 'Otp'

    name = fields.Char(string='name')
    otp_name = fields.Char(string="Otp name", readonly=True)
    is_used = fields.Boolean(string="Is otp used?", readonly=True)
    user_email = fields.Char(string="Login user email", readonly=True)

    def send_otp_mail(self, otp, login, name):
        template = self.env.ref('bi_website_otp_auth.send_otp_email_template', False)
        ctx = self.env.context.copy()
        user = self.env['res.users'].sudo().search([('login','=',login)])
        otp_config_id = self.env['website.otp'].sudo().search([], limit=1)
        if user.partner_id.name:
            ctx['partner_name'] = user.partner_id.name
        elif name:
            ctx['partner_name'] = name
        else:
            ctx['partner_name'] = 'User'
        ctx['partner_email'] = login
        ctx['email'] = otp_config_id.email
        template.with_context(ctx).sudo().send_mail(self.id, force_send=True)