# -*- coding: utf-8 -*-

import datetime
import time
import pytz
from odoo import models, fields, api, SUPERUSER_ID, _
# from odoo.exceptions import UserError, Warning
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

class PosConfig(models.Model):
    _inherit = "pos.config"

    @api.model
    def _custom_get_date_formats(self):
        """This method return current user language relatd date format and time format"""
        lang = get_lang(self.env)
        return (lang.date_format, lang.time_format)

    def custom_time_to_min(self, hour, minute):
        """Calculates total minutes based on hour and minute
            param hour: it's hour by close start time field on custom.pos.lock.period.
            param minute: it's minute by close start time field on custom.pos.lock.period.
            For Example:
                hour: 20
                minute: 30
                return: 1230
        """
        return hour*60+minute

    def custom_utc_to_local(self, utc_dt, pos_lock_config_id):
        """Converted getting date to the POS setting time zone
            param utc_dt: The close_start_datetime, close_end_datetime value in POS setting
            param pos_lock_config_id: The POS setting browse record
            For Example:
               utc_dt: 2019-12-24 05:08:20
               POS setting time zone: Asia/Kolkata
               return: 2019-12-24 10:38:20+05:30
        """
        local_tz = pytz.timezone(pos_lock_config_id.tz)
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)

    def custom_convert_custom_datetime(self, current_datetime_now, datetime_format):
        """Convert a different different datetime format to '%Y-%m-%d %H:%M:%S'
            param current_datetime_now: The record of  datetime type
            param datetime_format: The format of  datetime type record
            For Example:
                current_datetime_now: 2019-12-25 07:45:18.722355+05:30 (type: datetime.datetime) 
                datetime_format: %Y-%m-%d %H:%M:%S.%f
                return: 2019-12-25 07:45:18
        """
        only_date = current_datetime_now.date()
        only_time = current_datetime_now.time()
        current_datetime_now = str(only_date) + ' ' + str(only_time)
        current_datetime_now = datetime.datetime.strptime(current_datetime_now, datetime_format)
        myFormat = "%Y-%m-%d %H:%M:%S"
        current_datetime_now = current_datetime_now.strftime(myFormat)
        current_datetime_now = datetime.datetime.strptime(current_datetime_now, myFormat)
        return current_datetime_now

    def custom_check_pos_lock_period(self):
        """
            Showing the warning message based on condition
            
            - Search 'Lock Point of Sale' record by current pos config record, state, company base.
            - Show message based on received result.
            For Example:
                1) Your 'Lock point of sale' Lock Period Type is time wise.
                    - 'Lock point of sale' close start time and close end time value.
                        Close Start Time: 20:30
                        Close End Time: 08:30
                        Your Current Time: 07:00
                    - Get a number of hour and minutes using divmod function.
                    - Geting hour and minutes pass for custom_time_to_min menthod
                    - This method return a total of minutes.
                    - Warning message shows if your current time falls between 'close start time and close end time'.

                2) Your 'Lock point of sale' Lock Period Type is Date wise.
                    - 'Lock point of sale' close start time and close end time value.
                        Close Start Date: 12/25/2019
                        Close End Date: 12/31/2019
                        Your Current Date: 12/27/2019
                    - Warning message shows if your current date falls between 'close start date and close end date'.

                3) Your 'Lock point of sale' Lock Period Type is Datetime wise.
                    - 'Lock point of sale' close start datetime and close start datetime value.
                        Close Start Datetime: 12/25/2019 08:30:05
                        Close End Datetime: 12/31/2019 20:30:47
                        Your Current Datetime: 12/27/2019 07:59:32
                    - Convert a datetime to 'lock point sale' time zone using custom_utc_to_local method.
                    - Converts the result found by the custom_utc_to_local method to a '%Y-%m-%d %H:%M:%S' datetime format using custom_convert_custom_datetime method.
                    - Warning message shows if your current datetime falls between 'close start datetime and close endtime date'.

                4) Your 'Lock point of sale' Lock Period Type is Days wise.
                    - 'Lock point of sale' Days value.
                        Days: Friday
                        Your Current Days: Friday
                    - A warning message shows if your current day and alignment days are the same.
        """
        ctx = self._context.copy()
        if not ctx.get('special_no_warning', False):
            pos_lock_config_ids = self.env['custom.pos.lock.period'].search([
                ('pos_config_id', '=', self.id),
                ('state', '=', 'activate'),
                ('company_id', '=', self.env.user.company_id.id),
                ('allowed_user_ids', 'not in', self.env.user.id),
            ])
            try:
                tz = pytz.timezone(self.env.user.tz)
            except:
                superuser_id = self.env['res.users'].browse(SUPERUSER_ID)
                tz = pytz.timezone(superuser_id.tz)
            current_datetime_now = datetime.datetime.now(tz)
            date_format, time_format = self._custom_get_date_formats()
            for pos_lock_config_id in pos_lock_config_ids:
                if pos_lock_config_id and pos_lock_config_id.period_type == 'time':
                    start_time = pos_lock_config_id.close_start_time
                    end_time = pos_lock_config_id.close_end_time
                    time_now = current_datetime_now.time()
                    start_hours, start_minutes = divmod(start_time*60, 60)
                    open_time = self.custom_time_to_min(int(start_hours), int(start_minutes))
                    end_hours, end_minutes = divmod(end_time*60, 60)
                    close_time = self.custom_time_to_min(int(end_hours), int(end_minutes))
                    current_time = self.custom_time_to_min(time_now.hour, time_now.minute)

                    # if current_time < open_time and current_time > close_time:
                    #     pass
                    # else:
                    #     starting_time = str(int(start_hours)) + ':' + str(int(start_minutes))
                    #     endding_time = str(int(end_hours)) + ':' + str(int(end_minutes))

                    #     raise UserError(_("You cannot begin New Session/Resume this session during %s to %s time period because this period is locked by 'Lock Point of Sale (%s)' setting." %(starting_time, endding_time, pos_lock_config_id.id)))
                    
                    if current_time >= open_time and current_time < close_time:
                        starting_time = str(int(start_hours)) + ':' + str(int(start_minutes))
                        endding_time = str(int(end_hours)) + ':' + str(int(end_minutes))

                        raise UserError(_("You cannot begin New Session/Resume this session during %s to %s time period because this period is locked by 'Lock Point of Sale (%s)' setting." %(starting_time, endding_time, pos_lock_config_id.id)))

                if pos_lock_config_id and pos_lock_config_id.period_type == 'date':
                    close_start_date = pos_lock_config_id.close_start_date
                    close_end_date = pos_lock_config_id.close_end_date
                    current_date = current_datetime_now.date()

                    if close_start_date <= current_date and current_date <= close_end_date:
                        raise UserError(_("You cannot begin New Session/Resume this session during '%s' to '%s' date period because this period is locked by 'Lock Point of Sale (%s)' setting." %(close_start_date.strftime(date_format), close_end_date.strftime(date_format), pos_lock_config_id.id)))
                
                if pos_lock_config_id and pos_lock_config_id.period_type == 'datetime':
                    close_start_datetime = self.custom_utc_to_local(pos_lock_config_id.close_start_datetime, pos_lock_config_id)
                    close_start_datetime = self.custom_convert_custom_datetime(close_start_datetime, '%Y-%m-%d %H:%M:%S')
                    close_end_datetime = self.custom_utc_to_local(pos_lock_config_id.close_end_datetime, pos_lock_config_id)
                    close_end_datetime = self.custom_convert_custom_datetime(close_end_datetime, '%Y-%m-%d %H:%M:%S')
                    current_datetime_now = self.custom_convert_custom_datetime(current_datetime_now, '%Y-%m-%d %H:%M:%S.%f')
                    if current_datetime_now > close_start_datetime and current_datetime_now < close_end_datetime:
                        close_start_date_str = close_start_datetime.strftime(date_format)
                        close_start_time_str = close_start_datetime.strftime(time_format)
                        close_end_date_str = close_end_datetime.strftime(date_format)
                        close_end_time_str = close_end_datetime.strftime(time_format)
                        raise UserError(_("You cannot begin New Session/Resume this session during '%s %s' to '%s %s' datetime period because this period is locked by 'Lock Point of Sale (%s)' setting." %(close_start_date_str, close_start_time_str, close_end_date_str, close_end_time_str, pos_lock_config_id.id)))

                if pos_lock_config_id and pos_lock_config_id.period_type == 'days':
                    if current_datetime_now.weekday() == int(pos_lock_config_id.close_day):
                        raise UserError(_("This session is locked for '%s' because configuration on 'Lock Point of Sale (%s)' setting." %(current_datetime_now.strftime("%A"), pos_lock_config_id.id)))
        return True

    # Methods to open the POS override
    def open_ui(self):
        self.ensure_one()
        self.custom_check_pos_lock_period()
        return super(PosConfig, self).open_ui()