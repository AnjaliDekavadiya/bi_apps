# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    is_checkout_signup = fields.Boolean(string="Signup On Website Checkout Page", default=True)
