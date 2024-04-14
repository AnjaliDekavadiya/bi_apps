# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class ResSettingSale(models.TransientModel):
    _inherit = 'res.config.settings'

    is_checkout_signup = fields.Boolean(related="website_id.is_checkout_signup", string="Signup On Website Checkout Page", readonly=False)
