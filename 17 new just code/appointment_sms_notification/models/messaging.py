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
from odoo.exceptions import  UserError, RedirectWarning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date,datetime,timedelta
import dateutil,pytz
from dateutil.relativedelta import relativedelta
from urllib3.exceptions import HTTPError
import logging
DateTimeFormat = '%Y-%m-%d %H:%M:%S'
_logger = logging.getLogger(__name__)

class Appointment(models.Model):
    _inherit = "appointment"

    is_reminder_sms_sent = fields.Boolean("Reminder SMS Send", copy=False)
    enable_sms_reminder = fields.Boolean('Allow SMS Notification', default=True,
        help="Enable to allow SMS Notifications on this appointment", copy=True)

    @api.model_create_multi
    def create(self,vallst):
        for vals in vallst:
            appointment = super(Appointment,self).create(vals)
            appointment.with_context(create_appoint=1).send_sms_notification()
        return appointment

    def button_approve_appoint(self):
        res = super(Appointment,self).button_approve_appoint()
        for rec in self:
            rec.with_context(update_status=1).send_sms_notification()
        return res

    def button_set_to_pending(self):
        res = super(Appointment,self).button_set_to_pending()
        for rec in self:
            rec.with_context(update_status=1).send_sms_notification()
        return res

    def button_done_appoint(self):
        res = super(Appointment,self).button_done_appoint()
        for rec in self:
            rec.with_context(update_status=1).send_sms_notification()
        return res

    def button_reject_appoint(self):
        res = super(Appointment,self).button_reject_appoint()
        for rec in self:
            rec.with_context(update_status=1).send_sms_notification()
        return res

    def send_sms_notification(self):
        config_setting_obj = self.env['res.config.settings'].sudo().get_values()

        # Notify to customer on appointment create
        if self._context.get("create_appoint") and config_setting_obj.get("enable_sms_notify_on_creation") and config_setting_obj.get("sms_notify_on_creation", False):
            sms_template_obj = self.env['wk.sms.template'].browse(config_setting_obj.get("sms_notify_on_creation", False))
            if sms_template_obj:
                
                sms_template_obj.notify_appoint_via_sms_to_customer(self.customer, self)

        # Notify to customer on appointment Status update
        if self._context.get("update_status") and config_setting_obj.get("enable_sms_notify_on_status_upd") and config_setting_obj.get("sms_notify_on_status_upd", False):
            sms_template_obj = self.env['wk.sms.template'].browse(config_setting_obj.get("sms_notify_on_status_upd", False))
            if sms_template_obj:
                sms_template_obj.notify_appoint_via_sms_to_customer(self.customer, self)

        # Notify to customer on appointment Status update
        if self.enable_sms_reminder and self._context.get("notify_reminder") and config_setting_obj.get("enable_sms_notify_reminder") and config_setting_obj.get("sms_notify_reminder", False):
            send_sms_now = False
            # Check if reminder mail need to be send before days
            if self.appoint_state == 'approved' and self.remind_time and self.remind_in == 'days' and not self.is_reminder_sms_sent:
                current_day = date.today()
                later_day = datetime.strptime(str(self.appoint_date),"%Y-%m-%d").date() - timedelta(days=self.remind_time)
                time_diff = relativedelta(later_day, current_day)
                if time_diff.days ==  0 and time_diff.months == 0 and time_diff.years == 0:
                    send_sms_now = True

            # Check if reminder mail need to be send before hours
            if self.time_from and self.appoint_state == 'approved' and self.remind_time and self.remind_in == 'hours' and not self.is_reminder_sms_sent:
                time_diff = relativedelta(datetime.strptime(str(self.appoint_date),"%Y-%m-%d").date(), date.today())
                if time_diff.days ==  0 and time_diff.months == 0 and time_diff.years == 0:
                    start_time_minus_remind_time_hours = int(str(self.time_from).split('.')[0])
                    start_time_minus_remind_time_hours = int((start_time_minus_remind_time_hours + 24 -self.remind_time)%24)

                    current_time = datetime.now().replace(microsecond=0).replace(second=0)
                    user_tz = pytz.timezone(self.env.user.tz or 'UTC')
                    current_time = pytz.utc.localize(current_time).astimezone(user_tz).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    current_time = datetime.strptime(str(current_time), '%Y-%m-%d %H:%M:%S')
                    if current_time.hour == start_time_minus_remind_time_hours:
                        send_sms_now = True

            sms_template_obj = self.env['wk.sms.template'].browse(config_setting_obj.get("sms_notify_reminder", False))
            if send_sms_now and sms_template_obj:
                sms_template_obj.notify_appoint_via_sms_to_customer(self.customer, self)
                self.is_reminder_sms_sent = True
        return True

    @api.model
    def send_mail_for_reminder_scheduler_queue(self):
        _logger.info("SCHEDULER===============++++++++++++")
        res = super(Appointment, self).send_mail_for_reminder_scheduler_queue()
        obj = self.search([])
        for rec in obj:
            rec.with_context(notify_reminder=1).send_sms_notification()
        return res
