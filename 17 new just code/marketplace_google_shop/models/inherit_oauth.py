# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class Oauth2Detail(models.Model):
    _inherit = 'oauth2.detail'

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', default=_set_seller_id)
    domain_uri = fields.Char(string="Google Shop URL", help="Domain where You what google to authenticate")

    @api.onchange('marketplace_seller_id')
    def onchange_mp_seller(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if self.marketplace_seller_id and self.marketplace_seller_id.url_handler:
            self.domain_uri = base_url + '/' + self.marketplace_seller_id.url_handler
        else:
            self.domain_uri = None
