from . import models

def install_hook(env):
    for rec in env['res.partner'].search([('is_company', '=', False)]):
        if not rec.ks_user_id:
            rec.ks_user_id = rec.create_uid
