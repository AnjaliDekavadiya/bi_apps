# -*- coding: utf-8 -*-
##############################################################################
#
#    TL Technology
#    Copyright (C) of TL Technology (<https://www.posodoo.com>).
#    Odoo Proprietary License v1.0 along with this program.
#
##############################################################################
from odoo import api, fields, models, tools, _

class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_company(self):
        result = super()._loader_params_res_company()
        result['search_params']['fields'].extend(
            ['write_date'])
        return result