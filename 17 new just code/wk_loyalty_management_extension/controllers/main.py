# -*- coding: utf-8 -*-
##########################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>;)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>;
##########################################################################

from odoo import http
import logging
import json
_logger = logging.getLogger(__name__)
from odoo.osv import expression
from odoo.http import request
from odoo import api, fields, models
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController

class SaleCombinationInfo(WebsiteSaleVariantController):
    @http.route(auth='public')
    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, parent_combination=None, **kwargs):
        response = super(SaleCombinationInfo, self).get_combination_info_website(product_template_id,
        product_id, combination, add_qty, parent_combination, **kwargs)
        combination = request.env['product.template.attribute.value'].sudo().browse(combination)
        p_id = request.env['product.template'].sudo().browse(int(product_template_id))
        variant = p_id.sudo()._get_variant_for_combination(combination)
        data = request.env['website']._get_loyalty_points( variant,add_qty)
        obj=request.env['sale.order'].sudo()._get_default_wk_loyalty_program_id()
        if obj:
            loyalty_base = request.env['website.loyalty.management'].browse(int(obj)).loyalty_base
            response.update({'loyalty_base':loyalty_base})
        
        if data:
            response.update({'total_points':str(data.get('total'))})
            return response
        else:
            return response













