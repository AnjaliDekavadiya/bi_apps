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

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mp_auto_event_approve = fields.Boolean(string="Auto Event Approve")
    enable_notify_admin_on_event_approve_reject = fields.Boolean(
        string="Enable Notification Admin On Event Approve Reject")
    enable_notify_seller_on_event_approve_reject = fields.Boolean(
        string="Enable Notification Seller On Event Approve Reject")
    notify_admin_on_event_approve_reject_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Admin On Event Approve/Reject", domain="[('model_id.model','=','event.event')]")
    notify_seller_on_event_approve_reject_m_tmpl_id = fields.Many2one(
        "mail.template", string="Mail Template to Notify Seller On Event Approve/Reject", domain="[('model_id.model','=','event.event')]")


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set('res.config.settings', 'mp_auto_event_approve', self.mp_auto_event_approve)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_admin_on_event_approve_reject', self.enable_notify_admin_on_event_approve_reject)
        self.env['ir.default'].sudo().set('res.config.settings', 'enable_notify_seller_on_event_approve_reject', self.enable_notify_seller_on_event_approve_reject)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_admin_on_event_approve_reject_m_tmpl_id', self.notify_admin_on_event_approve_reject_m_tmpl_id.id)
        self.env['ir.default'].sudo().set('res.config.settings', 'notify_seller_on_event_approve_reject_m_tmpl_id', self.notify_seller_on_event_approve_reject_m_tmpl_id.id)
        return True
    
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        mp_auto_event_approve = IrDefault._get('res.config.settings', 'mp_auto_event_approve')
        enable_notify_admin_on_event_approve_reject = IrDefault._get('res.config.settings', 'enable_notify_admin_on_event_approve_reject')
        enable_notify_seller_on_event_approve_reject = IrDefault._get('res.config.settings', 'enable_notify_seller_on_event_approve_reject')
        notify_admin_on_event_approve_reject_m_tmpl_id = IrDefault._get('res.config.settings', 'notify_admin_on_event_approve_reject_m_tmpl_id')
        notify_seller_on_event_approve_reject_m_tmpl_id = IrDefault._get('res.config.settings', 'notify_seller_on_event_approve_reject_m_tmpl_id')
        res.update({
            'mp_auto_event_approve': mp_auto_event_approve,
            'enable_notify_admin_on_event_approve_reject': enable_notify_admin_on_event_approve_reject,
            'enable_notify_seller_on_event_approve_reject' : enable_notify_seller_on_event_approve_reject,
            'notify_admin_on_event_approve_reject_m_tmpl_id' : notify_admin_on_event_approve_reject_m_tmpl_id,
            'notify_seller_on_event_approve_reject_m_tmpl_id' : notify_seller_on_event_approve_reject_m_tmpl_id,
        })
        return res