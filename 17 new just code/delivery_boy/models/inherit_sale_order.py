# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
from odoo import models,fields,api, _

import logging
_logger = logging.getLogger(__name__)

class InheritSaleOrder(models.Model):
    _inherit="sale.order"

    order_type=fields.Selection(selection=[('prepaid','Pre Paid'),('postpaid','Post Paid')])

    def action_confirm(self):
        if self.transaction_ids and self.transaction_ids[0].provider_id.mobikul_payment_type == 'postpaid':
            self.order_type='postpaid'
        else:
            self.order_type='prepaid'
        res = super(InheritSaleOrder, self).action_confirm()
        return res
