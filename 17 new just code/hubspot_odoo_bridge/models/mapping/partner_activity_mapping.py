from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)

class MappingActivity(models.Model):
    _inherit = "res.partner.mapping"

    # activity = fields.One2many('hubspot.activity.mapping','connection_id','Activity Mappings',domain=[('object_type','=','product')])
    activity = fields.One2many('hubspot.activity.mapping','crm_partner_id','Activity Mappings')