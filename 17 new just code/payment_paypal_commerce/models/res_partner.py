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

class ResPartner(models.Model):
    _inherit = "res.partner"

    commerce_tracking_id = fields.Char("Paypal Tracking ID")
    commerce_merchant_id = fields.Char("Paypal Merchant ID")
    primary_email_confirmed = fields.Boolean("Primary Email Confirmed")
    commerce_authorized = fields.Boolean("Authorized From Paypal")
