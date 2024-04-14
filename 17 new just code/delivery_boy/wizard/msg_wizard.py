# -*- coding: utf-8 -*-
#################################################################################
# Author : Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
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
# If not, see <https://store.webkul.com/license.html/>;
#################################################################################


from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class MessageWizard(models.TransientModel):
    _name = 'msg.wizard'
    _description = 'wizard msg'

    text = fields.Text()

class AuthenticationWarningWizard(models.TransientModel):
    _name = 'authentication.warning.wizard'
    _description = "Authentication warning wizard"

    def setDeliveryBoyInactive(self):
        partnerObjs = self.env['res.partner'].search([('is_delivery_boy','=',True)])
        for partnerObj in partnerObjs:
            partnerObj.write({'delivery_boy_status': 'offline','is_delivery_boy': False})
            fcmObjs = self.env['delivery.boy.fcm.registered.devices'].search([('partner_id','=',partnerObj.id)])
            for fcmObj in fcmObjs:
                fcmObj.partner_id = False


    def force_reset_authentication_object(self):
        active_id = self.env.context.get('active_id')
        data = self.env['delivery.boy.config'].browse(active_id)
        if data.authentication_type == "user":
            data.authentication_type = "employee"
            self.setDeliveryBoyInactive()
        else:
            data.authentication_type = "user"
            self.setDeliveryBoyInactive()
