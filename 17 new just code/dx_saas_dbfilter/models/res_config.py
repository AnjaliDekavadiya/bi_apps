# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    grace_period = fields.Char(string="Grace Period", config_parameter="dx_saas_dbfilter.grace_period", default=0,
                               required=True)
    create_ssl_for_website_purchases = fields.Boolean(string="Enable ssl for website purchases",
                                                      config_parameter="dx_saas_dbfilter.create_ssl_for_website_purchases",
                                                      required=True)
    saas_client_domain_start = fields.Char(string="Domain Start",
                                           config_parameter="dx_saas_dbfilter.saas_client_domain_start",
                                           required=True)
