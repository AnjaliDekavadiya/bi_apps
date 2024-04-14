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
import logging
_logger = logging.getLogger(__name__)
from odoo.addons.marketplace_hyperlocal_system.controllers.main import WebsiteSale

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search_get_detail(self, website, order, options):
        res = super(ProductTemplate, self)._search_get_detail(website, order, options)
        if not website.enable_hyperlocal:
            return res
        sellerIds = None
        latLong = self.env['seller.ship.rate'].sudo().getdefaultLongLat()
        if latLong:
            sellerShipAreaObjs = self.env['seller.ship.area'].sudo().search([])
            sellerIds = WebsiteSale().getAvailableSellers(sellerShipAreaObjs, latLong)

        domain = res['base_domain']
        # seller_ids = options.get('hyperlocal_seller_ids')
        if sellerIds:
            domain.append(['|',('marketplace_seller_id','=',False),('marketplace_seller_id','in',sellerIds)])
        else:
            domain.append([('marketplace_seller_id','=',False)])
        return res
