from odoo import api, fields, models, _


class WhatsappTemplates(models.Model):
    _inherit = 'whatsapp.templates'

    marketing_template = fields.Boolean(string='Marketing Template')
    whatsapp_marketing_id = fields.Many2one('whatsapp.marketing', string='Mass Messages')

