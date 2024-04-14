from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('pragtech_facebook_messenger.activate_facebook', self.activate_facebook)
        self.env['ir.config_parameter'].set_param('pragtech_facebook_messenger.facebook_app_id',
                                                  self.facebook_app_id)
        self.env['ir.config_parameter'].set_param('pragtech_facebook_messenger.facebook_app_secret',
                                                  self.facebook_app_secret)
        self.env['ir.config_parameter'].set_param('pragtech_facebook_messenger.facebook_page_id',
                                                  self.facebook_page_id)
        self.env['ir.config_parameter'].set_param('pragtech_facebook_messenger.facebook_page_access',
                                                  self.facebook_page_access)
        self.env['ir.config_parameter'].set_param('pragtech_facebook_messenger.facebook_verify_token',
                                                  self.facebook_verify_token)
        # self.env['ir.config_parameter'].set_param('pragtech_facebook_messenger.module_facebook_webhook_verify',
        #                                           self.module_facebook_webhook_verify)
        self.env['ir.config_parameter'].set_param('pragtech_facebook_messenger.webhook_type',
                                                  self.webhook_type)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        activate_facebook = self.env['ir.config_parameter'].sudo().get_param('pragtech_facebook_messenger.activate_facebook')
        facebook_app_id = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_facebook_messenger.facebook_app_id')
        facebook_app_secret = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_facebook_messenger.facebook_app_secret')
        facebook_page_id = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_facebook_messenger.facebook_page_id')
        facebook_page_access = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_facebook_messenger.facebook_page_access')
        facebook_verify_token = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_facebook_messenger.facebook_verify_token')
        # module_facebook_webhook_verify = self.env['ir.config_parameter'].sudo().get_param(
        #     'pragtech_facebook_messenger.module_facebook_webhook_verify')
        res.update(
            activate_facebook=activate_facebook,
            facebook_app_secret=facebook_app_secret,
            facebook_app_id=facebook_app_id,
            facebook_page_id=facebook_page_id,
            facebook_page_access=facebook_page_access,
            facebook_verify_token=facebook_verify_token,
            # module_facebook_webhook_verify=module_facebook_webhook_verify
        )
        return res

    activate_facebook = fields.Boolean(string="Activate Facebook")
    facebook_app_id = fields.Char(string='App ID')
    facebook_page_id = fields.Char(string="Facebook page ID")
    facebook_app_secret = fields.Char(string='App Secret')
    facebook_page_access = fields.Char(string="Page Access token")
    facebook_verify_token = fields.Char(string="Webhook verify token")
    # module_facebook_webhook_verify = fields.Boolean(string="verify webhook")
    webhook_type = fields.Char(string="webhook type", default='json')
