# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class WebsiteOtp(models.Model):
    _name = 'website.otp'
    _description = 'Website Otp'

    name = fields.Char(string="name")
    signin_auth = fields.Boolean(string="Sign-in Authentication")
    signup_auth = fields.Boolean(string="Sign-up Authentication")
    otp_auth_limit = fields.Integer(string="Otp time limit")
    otp_auth_type = fields.Selection([('text', 'Text'), ('password', 'Password')], default='text', string="Otp Type")
    email = fields.Char(string="Email", help="Set email for send otp from particular email")
