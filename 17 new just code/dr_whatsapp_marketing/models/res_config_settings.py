from odoo import api, models, fields, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_access_token = fields.Char(string='Access Token', config_parameter='whatsapp.access_token')
    whatsapp_app_id = fields.Char(string='App ID', config_parameter='whatsapp.app_id')
    whatsapp_app_secret = fields.Char(string='App Secret', config_parameter='whatsapp.app_secret')
    whatsapp_api_version = fields.Char(string='API Version', config_parameter='whatsapp.api_version')
    whatsapp_phone_id = fields.Char(string='Phone Number', config_parameter='whatsapp.phone_id')
    whatsapp_business_id = fields.Char(string='Business Number', config_parameter='whatsapp.business_id')
    whatsapp_verify_token = fields.Char(string='Verify Token', config_parameter='whatsapp.verify_token')

    # def set_values(self):
    #     config_parameters = self.env['ir.config_parameter'].sudo()
    #     config_parameters.set_param('whatsapp.access_token', self.whatsapp_access_token)
    #     config_parameters.set_param('whatsapp.app_id', self.whatsapp_app_id)
    #     config_parameters.set_param('whatsapp.app_secret', self.whatsapp_app_secret)
    #     config_parameters.set_param('whatsapp.api_version', self.whatsapp_api_version)
    #     config_parameters.set_param('whatsapp.phone_id', self.whatsapp_phone_id)
    #     config_parameters.set_param('whatsapp.business_id', self.whatsapp_business_id)
    #     config_parameters.set_param('whatsapp.verify_token', self.whatsapp_verify_token)

    # def get_values(self):
    #     config_parameters = self.env['ir.config_parameter'].sudo()
    #     config_parameters['whatsapp_access_token'] = config_parameters.get_param('whatsapp.access_token')
    #     config_parameters['whatsapp_app_id'] = config_parameters.get_param('whatsapp.app_id')
    #     config_parameters['whatsapp_app_secret'] = config_parameters.get_param('whatsapp.app_secret')
    #     config_parameters['whatsapp_api_version'] = config_parameters.get_param('whatsapp.api_version')
    #     config_parameters['whatsapp_phone_id'] = config_parameters.get_param('whatsapp.phone_id')
    #     config_parameters['whatsapp_business_id'] = config_parameters.get_param('whatsapp.business_id')
    #     config_parameters['whatsapp_verify_token'] = config_parameters.get_param('whatsapp.verify_token')
    #     return config_parameters