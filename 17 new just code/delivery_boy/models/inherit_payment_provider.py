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
import logging
_logger = logging.getLogger(__name__)

from odoo import models,fields,api, _

class InheritPaymentAcquirer(models.Model):
    _inherit="payment.provider"

    mobikul_payment_type = fields.Selection([
        ('prepaid', 'Pre Paid'),
        ('postpaid', 'Post Paid')],
        string='Payment Type',
        default='prepaid')
