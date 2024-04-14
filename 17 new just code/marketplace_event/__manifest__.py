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
  "name"                 :  "Odoo Marketplace Events Management",
  "summary"              :  """Odoo Marketplace Event Management provides feature for admin and seller to create events accordingly for the Marketplace.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  20,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo.html",
  "description"          :  """Event, Event Manager, Event Management, Seller Wise Event""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_event&custom_url=/event",
  "depends"              :  [
                             'odoo_marketplace',
                             'website_event',
                             'event_sale',
                            ],
  "data"                 :  [
                            'security/access_control_security.xml',
                            'security/ir.model.access.csv',
                            'edi/event_status_change_mail_to_admin.xml',
                            'edi/event_status_change_mail_to_seller.xml',
                            'views/res_partner_view.xml',
                            'views/attendee.xml',
                            'views/mp_events_view.xml',
                            'views/res_config.xml',
                            'views/inherit_mp_dashboard.xml',
                            'views/product_view.xml',
                            'views/seller_view.xml',
                            'data/mp_dashboard_data.xml',
                            'data/mp_config_setting_data.xml',
                            ],
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  199,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}