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
  "name"                 :  "Odoo Marketplace Seller Credit Management System",
  "summary"              :  """Now seller can provide Credit Points for Loyal Customers""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "",
  "description"          :  """Loyalty Management
                              Credit Management""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_seller_credit_system&lifetime=120&lout=0&custom_url=/shop",
  "depends"              :  ['marketplace_seller_wise_checkout',
                            'website_loyalty_management'
                            ],
                             
  "data"                 :  [
                            'security/ir.model.access.csv',
                            'wizard/wk_publish_confirmation.xml',
                            'views/mp_seller_credit.xml',
                            'views/template.xml',
                            'data/data.xml',
                            ],
  "images"               :  ["static/description/Banner.gif"],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
