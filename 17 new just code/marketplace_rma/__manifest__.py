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
  "name"                 :  "Marketplace Return Merchandise Authorization (RMA)",
  "summary"              :  """Marketplace Return merchandise authorization module helps admin and sellers to manage product returns.""",
  "category"             :  "Marketplace",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-RMA.html",
  "description"          :  """Marketplace RMA
Return merchandise authorization""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_rma&lifetime=120&lout=1&custom_url=/",
  "depends"              :  [
                             'odoo_marketplace',
                             'rma',
                            ],
  "data"                 :  [
                             'security/marketplace_rma_security.xml',
                             'security/ir.model.access.csv',
                             'wizard/product_return_view.xml',
                             'wizard/new_delivery_order.xml',
                             'views/rma_view.xml',
                             'views/templates.xml',
                             'views/marketplace_config_view.xml',
                             'views/res_partner_view.xml',
                             'data/rma_mail_to_seller.xml',
                             'data/mp_config_settings_data.xml',
                            ],
  "images"               :  ['static/description/Banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  69,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
