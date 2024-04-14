#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _
from odoo.addons.website_voucher.models.inherited_website import Website as WB

import logging
_logger = logging.getLogger(__name__)


@api.model
def sale_get_order(self, force_create=False,update_pricelist=False, context=None):
    sale_order = super(WB, self).sale_get_order(force_create, update_pricelist)
    order_total_price = 0
    voucher_obj = self.get_current_order_voucher(sale_order)
    if voucher_obj and force_create:
        if hasattr(sale_order,'order_line'):
            voucher_product_id = self.wk_get_default_product()
            if isinstance(voucher_product_id, (list)):
                voucher_product_id = voucher_product_id[0]
            res = self.get_voucher_product_price(sale_order,voucher_obj, voucher_product_id)
            selected_prod_percent_price = res['selected_prod_percent_price']
            order_total_price = res['order_total_price']
            self.set_voucher_sale_order_price(sale_order, voucher_obj,voucher_product_id, selected_prod_percent_price,voucher_obj.id,order_total_price)
    return sale_order

WB.sale_get_order = sale_get_order
