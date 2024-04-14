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
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _

class PaymentAcquirer(models.Model):
    _inherit = 'payment.provider'

    product_paypal = fields.Boolean("Enable on Product Page")
    cart_paypal = fields.Boolean("Enable on Cart Page")
    enable_for_public = fields.Boolean("Enable for Public User")
