from odoo import api, fields, models

class OpenAIConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openai_api_key = fields.Char(string='OpenAI API Key')
    openai_api_engine = fields.Selection([
        ('odoo', 'Odoo Free AI'),
        ('text-davinci-002', 'Davinci (text-davinci-002)'),
        ('text-davinci-003', 'Davinci (text-davinci-003)'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ('gpt-4', 'GPT-4'),
        ('gpt-4-32k', 'GPT-4 32k'),
        ('curie', 'Curie'),
        ('babbage', 'Babbage'),
        ('ada', 'Ada'),
        ('cursing', 'Cursing'), ]
        , string='Engine', default='odoo')

    openai_api_max_tokens = fields.Integer(string='Max Tokens', default=1000)


    @api.model
    def get_values(self):
        res = super(OpenAIConfigSettings, self).get_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        openai_api_key = config_parameter.get_param('openai_api_key')
        res.update(openai_api_key=openai_api_key)
        openai_api_engine = config_parameter.get_param('openai_api_engine') or 'text-davinci-002'
        res.update(openai_api_engine=openai_api_engine)
        openai_api_max_tokens = config_parameter.get_param('openai_api_max_tokens') or 1000
        res.update(openai_api_max_tokens=openai_api_max_tokens)
        return res

    def set_values(self):
        super(OpenAIConfigSettings, self).set_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        config_parameter.set_param('openai_api_key', self.openai_api_key)
        config_parameter.set_param('openai_api_engine', self.openai_api_engine)
        config_parameter.set_param('openai_api_max_tokens', self.openai_api_max_tokens)
