from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)

class MappingActivity(models.Model):
    _inherit = "crm.lead.mapping"

    # activity = fields.One2many('hubspot.activity.mapping','connection_id','Activity Mappings',domain=[('object_type','=','product')])
    activity = fields.One2many('hubspot.activity.mapping','crm_lead_id','Activity Mappings')