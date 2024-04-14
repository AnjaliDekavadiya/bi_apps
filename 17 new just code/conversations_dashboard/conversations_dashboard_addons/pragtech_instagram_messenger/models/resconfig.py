from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('pragtech_instagram_messenger.instagram_app_secret',
                                                  self.instagram_app_secret)
        self.env['ir.config_parameter'].set_param('pragtech_instagram_messenger.instagram_page_access',
                                                  self.instagram_page_access)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_instagram_messenger.instagram_verify_token',
                                                         self.instagram_verify_token)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        instagram_app_secret = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_instagram_messenger.instagram_app_secret')
        instagram_page_access = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_instagram_messenger.instagram_page_access')
        instagram_verify_token = self.env['ir.config_parameter'].sudo().get_param(
            'pragtech_instagram_messenger.instagram_verify_token')
        res.update(
            instagram_app_secret=instagram_app_secret,
            instagram_page_access=instagram_page_access,
            instagram_verify_token=instagram_verify_token,
        )
        return res

    instagram_app_secret = fields.Char(string='Instagram App Secret')
    instagram_page_access = fields.Char(string="Instagram Page Access token")
    instagram_verify_token = fields.Char(string="Instagram Webhook verify token")
