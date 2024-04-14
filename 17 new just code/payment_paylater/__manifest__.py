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
  "name"                 :  "Payment Acquirer PayLater",
  "summary"              :  """Payment acquirer for paylater""",
  "category"             :  "Accounting",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/odoo-payment-acquirer-paylater.html",
  "description"          :  """Payment Acquirer: Pay Later implementation.""",
  "license"              :  "Other proprietary",
  "depends"              :  ['payment'],
  "data"                 :  [
                              'security/ir.model.access.csv',
                              'views/templates.xml',
                              'data/payment_acquirer_data.xml',
                            ],
  "images"               :  ['static/description/banner.png'],
  "installable"          :  True,
  "price"                :  10.0,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  'post_init_hook'       :  'post_init_hook',
  'uninstall_hook'       :  'uninstall_hook',
}