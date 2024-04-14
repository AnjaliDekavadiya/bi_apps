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
from odoo import tools, api
import logging,re
_logger = logging.getLogger(__name__)


class SmsTemplate(models.Model):
    "Templates for sending sms"
    _inherit = "wk.sms.template"
    _description = 'SMS Templates'
    _order = 'name'

    condition = fields.Selection(selection_add=[('appointment', 'Appointment'),])

    @api.depends('condition')
    def onchange_condition(self):
        for rec in self:
            if rec.condition:
                if rec.condition in ['appointment']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'appointment')])
                    rec.model_id = model_id.id if model_id else False
                else:
                    super(SmsTemplate, self).onchange_condition()
            else:
                super(SmsTemplate, self).onchange_condition()

    def notify_appoint_via_sms_to_customer(self, partner_id, obj):

        if not self:
            return False
        mobile = self.sudo()._get_partner_mobile(
            partner_id)
        if mobile:
            self.send_appoint_sms_using_template(mobile, self, obj=obj)

    @api.model
    def send_appoint_sms_using_template(self, mob_no, sms_tmpl, sms_gateway=None, obj=None):
        if not sms_gateway:
            gateway_id = self.env["sms.mail.server"].search(
                [], order='sequence asc', limit=1)
        else:
            gateway_id = sms_gateway
        if mob_no and sms_tmpl and obj:
            sms_sms_obj = self.env["wk.sms.sms"].create({
                'sms_gateway_config_id': gateway_id.id,
                'partner_id': obj.customer.id,
                'to': mob_no,
                'group_type': 'individual',
                'auto_delete': sms_tmpl.auto_delete,
                'msg': sms_tmpl.get_appoint_body_data(obj, obj.customer),
                'template_id': False
            })
            sms_sms_obj.send_sms_via_gateway(
                sms_sms_obj.msg, [sms_sms_obj.to], from_mob=None, sms_gateway=gateway_id)

    def get_appoint_body_data(self, obj, partner_id=None):
        self.ensure_one()
        if obj:
            body_msg = self.env["mail.template"].with_context(lang=partner_id.lang if partner_id else '').sudo()._render_template(
                self.sms_body_html, self.model, [obj.id])
            new_body_msg = re.sub("<.*?>", " ", body_msg[obj.id])
            return new_body_msg
            return " ".join(strip_tags(new_body_msg).split())
