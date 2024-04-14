import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class WhatsappMessages(models.Model):
    _inherit = 'whatsapp.messages'
    _description = 'Whatsapp Messages'

    whatsapp_contact_id = fields.Many2one('whatsapp.contact','Whatsapp Contact')
