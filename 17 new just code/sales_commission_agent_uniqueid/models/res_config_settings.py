# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custom_search_agent = fields.Selection(
        selection=[
            ('custom_agent_id','Select Agent from List'),
            ('have_an_agent_id','Add Agent by ID'),
        ],
        string="Agent Search Method on Web Shop",
        default="custom_agent_id",
        required=False
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['custom_search_agent'] = self.env['ir.config_parameter'].sudo().get_param('sales_commission_agent_uniqueid.custom_search_agent', default='custom_agent_id')

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('sales_commission_agent_uniqueid.custom_search_agent', self.custom_search_agent)

        super(ResConfigSettings, self).set_values()
