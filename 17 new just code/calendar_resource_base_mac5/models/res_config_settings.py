from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fc_premium_license = fields.Char(
        string="FullCalendar Permium License",
        config_parameter='calendar_resource_base_mac5.fc_premium_license',
    )
