from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    fleet_alert_phone = fields.Char("Fleet Alert Phone", tracking=True)