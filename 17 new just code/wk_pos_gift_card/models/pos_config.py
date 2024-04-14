# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import  ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    print_gift_card = fields.Boolean(default=True, string="Print Gift Card")


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('wk_is_gift_card')
        return result


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_print_gift_card = fields.Boolean(
        related='pos_config_id.print_gift_card', readonly=False)
