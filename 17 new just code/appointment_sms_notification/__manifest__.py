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
{
  "name"                 :  "Appointment SMS Notification Management",
  "summary"              :  """Provides facility to send notifications to customer using SMS.""",
  "category"             :  "industries",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Appointment-SMS-Notification-Management.html",
  "description"          :  """https://webkul.com/blog/odoo-appointment-sms-notification-management/""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=appointment_sms_notification",
  "depends"              :  [
                             'sms_notification',
                             'wk_appointment',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'edi/app_sms_template_for_reminder.xml',
                             'edi/app_sms_template_on_creation.xml',
                             'edi/app_sms_template_on_status_update.xml',
                             'views/res_config_view.xml',
                             'views/inherit_appoint_views.xml',
                             'data/appoint_sms_data.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  50,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
