# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request


class ResConfigSettings_Inherit(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_google_map = fields.Boolean('Enable Google Map', related="company_id.enable_google_map",readonly=False)
    google_maps_api_key_cust = fields.Char(string="Google Map API Key",related="company_id.google_maps_api_key",readonly=False)

class Res_company_inherit(models.Model):
    _inherit = 'res.company'

    enable_google_map = fields.Boolean('Enable Google Map')
    google_maps_api_key = fields.Char(string='Google Map API Key')


class POSConfig(models.Model):
    _inherit = 'pos.config'


    def get_google_map_key(self):
        return self.company_id.google_maps_api_key


class POSOrderLoad(models.Model):
    _inherit = 'pos.session'


    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()
        result['search_params']['fields'].extend(['enable_google_map','google_maps_api_key'])
        return result