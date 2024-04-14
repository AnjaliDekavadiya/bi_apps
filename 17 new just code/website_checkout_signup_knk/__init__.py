# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from . import models
from . import controllers


def _auto_website_signup_b2c(env):
    env['website'].search([]).write({'auth_signup_uninvited': 'b2c'})
