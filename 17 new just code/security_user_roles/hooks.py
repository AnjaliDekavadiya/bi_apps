# -*- coding: utf-8 -*-

def post_init_hook(env):
    """
    Introduced to update views after initializing the app
    """
    env["res.groups"].sudo()._update_security_role_view()
