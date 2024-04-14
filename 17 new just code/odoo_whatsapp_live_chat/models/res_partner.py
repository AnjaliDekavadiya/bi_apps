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

from odoo import models, fields,api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    whatsapp_support_member = fields.Boolean(string="Whatsapp Support Member")
    member_type = fields.Many2one(comodel_name="whatsapp.member.type", string="Member Type")
    time_from = fields.Float(string="Time From")
    time_to = fields.Float(string="Time To")
    status = fields.Selection([('active', 'Active'),('inactive','Inactive')], string="Whatsapp Chat Status", default="inactive")
    whatsapp_message = fields.Text(string="Message", help="Message to send on whatsapp", translate=True)

    def active_status(self):
        for rec in self:
            rec.status = 'active'

    def inactive_status(self):
        for rec in self:
            rec.status = 'inactive'

    try:
        import phonenumbers
        def _get_partner_mobile(self):
            if self.mobile[0] == '+':
                mobile_number = self.phonenumbers.parse(self.mobile, None)
                country_code = mobile_number.country_code
                national_number = mobile_number.national_number
            else:
                national_number = self.mobile
                if self.country_id and self.country_id.phone_code:
                    country_code = self.country_id.phone_code
                else:
                    country_code = self.env.user.company_id.country_id.phone_code
            mobile = str(country_code) + str(national_number)
            return mobile

    except ImportError:
        def _get_partner_mobile(self):
            _logger.info(
                "The `phonenumbers` Python module is not installed, contact numbers will not be "
                "verified. Please install the `phonenumbers` Python module."
            )
            return self.mobile

    @api.constrains('time_from','time_to')
    def time_validation(self):
        if self.time_from < 0 or self.time_from > 24:
            raise ValidationError("Time duration should be between 00:00 to 24:00")
        if self.time_to < 0 or self.time_to > 24:
            raise ValidationError("Time duration should be between 00:00 to 24:00")
        if self.time_from > self.time_to:
            raise ValidationError("Time From should be less than Time To")
