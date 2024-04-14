# -*- coding: utf-8 -*-

from . import models
from . import controllers

from odoo.addons.payment import setup_provider, reset_payment_provider


# def post_init_hook(cr, registry):
#     setup_provider(cr, registry, 'cod')

def post_init_hook(env):
    setup_provider(env, 'cod')


# def uninstall_hook(cr, registry):
#     reset_payment_provider(cr, registry, 'cod')

def uninstall_hook(env):
    reset_payment_provider(env, 'cod')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
