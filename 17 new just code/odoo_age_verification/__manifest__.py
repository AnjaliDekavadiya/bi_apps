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
  "name"                 :  "Odoo Age Verification",
  "summary"              :  """Admin can restrict user to access webpage without verify his/her age""",
  "category"             :  "Extra Tools",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "description"          :  """Enable/Disable age verification popup
    Enable date of birth option
    Set minimum age
    Add discriptions to display message to user
    Add terms and conditions""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=odoo_age_verification&custom_url=/",
  "depends"              :  ['website_webkul_addons'],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/template.xml',
                             'views/webkul_addons_config_inherit_view.xml',
                             'views/res_config_view.xml',
                            ],
  "assets"               : {
              "web.assets_frontend": [
                                'odoo_age_verification/static/src/css/age_verification.css',
                                'odoo_age_verification/static/src/js/age_verification.js',
                                'odoo_age_verification/static/src/js/date-dropdowns.js',
                              ],
                            },
  "demo"                 :  ['demo/age_verification_settings_demo.xml'],
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  35,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
