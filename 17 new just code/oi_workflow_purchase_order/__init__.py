from . import models
from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    env["purchase.order"]._create_approval_settings()

def uninstall_hook(env):
    env['approval.settings'].get("purchase.order").unlink()