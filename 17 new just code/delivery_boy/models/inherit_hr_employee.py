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

class InheritHrEmployee(models.Model):
    _inherit="hr.employee"

    is_delivery_boy = fields.Boolean(string="Is a Delivery Boy", copy=False, related='work_contact_id.is_delivery_boy')

    def toggle_is_delivery_boy(self):
        for user in self:
            if self.is_delivery_boy:
                self.work_contact_id.is_delivery_boy = False
            else:
                self.work_contact_id.is_delivery_boy = True
                self.work_contact_id.employee = True
