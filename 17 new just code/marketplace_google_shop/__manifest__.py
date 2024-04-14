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
  "name"                 :  "Odoo Marketplace Google Shop",
  "summary"              :  "Marketplace products can be synced with Google Merchant Center.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",
  "description"          :  """Marketplace products can be synced with Google Merchant Center.""",
  "depends"              :  [
                                'google_shop',
                                'odoo_marketplace',
                             ],
  "data"                 :  [
                              'security/ir.model.access.csv',
                              'security/mp_google_shop_security.xml',
                              'views/mp_google_shop_account_view.xml',
                              'views/mp_google_shop_field_view.xml',
                              'views/mp_google_shop_shop_view.xml',
                              'views/google_shop_menu.xml',
                            ],
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
