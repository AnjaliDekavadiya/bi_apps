from odoo import models, fields, api


class OfficeSettings(models.Model):
    _name = "ks_office365.settings"
    _rec_name = "rec_name"
    _description = "Store azure credentials and authentication module"

    rec_name = fields.Char("Settings", default="Office365 Authentication")
    ks_user = fields.Many2one("res.users", default=lambda self: self.env.user.id)

    ks_client_id = fields.Char("Client ID")
    ks_client_secret = fields.Char("Client Secret")
    ks_redirect_url = fields.Char("Redirect URL")
    ks_scope = fields.Char("Scope", default="")

    ks_office_login = fields.Boolean(default=False)
    ks_office_login_code = fields.Char(default=False)

    ks_allow_login = fields.Boolean("Login with Office 365", default=True)
    ks_create_new_user = fields.Boolean("Create new User", default=True,
                                        help="Create new Internal user if there is no existing user with login email "
                                             "matching the microsoft email")

    ks_dont_sync = fields.Boolean(default=False)
    ks_has_office_group = fields.Boolean(default=False)

    @api.model
    def ks_get_code_url(self):
        ks_admin = self.env['ks_office365.settings'].search([])
        ks_client_id = ks_admin.ks_client_id
        ks_redirect_url = ks_admin.ks_redirect_url
        ks_response_type = "code"
        ks_response_mode = "query"
        ks_state = "office_login"
        ks_scope = "offline_access User.Read"

        data = (ks_client_id, ks_response_type, ks_redirect_url, ks_scope, ks_response_mode, ks_state)
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=%s" \
              "&response_type=%s&redirect_uri=%s&scope=%s&response_mode=%s&state=%s" % data
        return url

    @api.model
    def ks_show_login_button(self):
        ks_auth_setting = self.env['ks_office365.settings'].search([], limit=1)
        if ks_auth_setting.ks_allow_login:
            return True
        else:
            return False
