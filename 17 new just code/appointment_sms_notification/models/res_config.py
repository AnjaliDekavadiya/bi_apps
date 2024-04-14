# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
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
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_sms_notify_reminder = fields.Boolean("Enable to send sms for Appointment Reminder")
    sms_notify_reminder = fields.Many2one(
        "wk.sms.template", string="Appointment Reminder Sms Template", domain="[('model_id.model','=','appointment')]")
    enable_sms_notify_on_creation = fields.Boolean("Enable to send sms on Appointment Creation")
    sms_notify_on_creation = fields.Many2one(
        "wk.sms.template", string="Appointment Creation Sms Template", domain="[('model_id.model','=','appointment')]")
    enable_sms_notify_on_status_upd = fields.Boolean("Enable to send sms on Appointment Status Update")
    sms_notify_on_status_upd = fields.Many2one(
        "wk.sms.template", string="Appointment Status Update Sms Template", domain="[('model_id.model','=','appointment')]")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings','enable_sms_notify_reminder', self.enable_sms_notify_reminder)
        IrDefault.set('res.config.settings','sms_notify_reminder', self.sms_notify_reminder.id)
        IrDefault.set('res.config.settings','enable_sms_notify_on_creation', self.enable_sms_notify_on_creation)
        IrDefault.set('res.config.settings','sms_notify_on_creation', self.sms_notify_on_creation.id)
        IrDefault.set('res.config.settings','enable_sms_notify_on_status_upd', self.enable_sms_notify_on_status_upd)
        IrDefault.set('res.config.settings','sms_notify_on_status_upd', self.sms_notify_on_status_upd.id)
        return True

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        temp1 = self.env['ir.model.data'].check_object_reference(
            'appointment_sms_notification', 'app_sms_template_for_reminder')[1]
        temp2 = self.env['ir.model.data'].check_object_reference(
            'appointment_sms_notification', 'app_sms_template_on_creation')[1]
        temp3 = self.env['ir.model.data'].check_object_reference(
            'appointment_sms_notification', 'app_sms_template_on_status_update')[1]
        res.update(
            {
            'enable_sms_notify_reminder': IrDefault._get('res.config.settings', 'enable_sms_notify_reminder'),
            'sms_notify_reminder': IrDefault._get('res.config.settings', 'sms_notify_reminder') or temp1,
            'enable_sms_notify_on_creation': IrDefault._get('res.config.settings', 'enable_sms_notify_on_creation'),
            'sms_notify_on_creation': IrDefault._get('res.config.settings', 'sms_notify_on_creation') or temp2,
            'enable_sms_notify_on_status_upd': IrDefault._get('res.config.settings', 'enable_sms_notify_on_status_upd'),
            'sms_notify_on_status_upd': IrDefault._get('res.config.settings', 'sms_notify_on_status_upd') or temp3,
            }
        )
        return res
